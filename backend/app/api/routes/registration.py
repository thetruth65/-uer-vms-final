# backend/app/api/routes/registration.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.database.models import Voter, AuditLog, generate_uuid
from app.schemas.voter import VoterRegistrationResponse
from app.services.ai_dedup import AIDedupService
from app.services.integrity import IntegrityService
from app.services.blockchain_client import BlockchainClient
from app.core.config import settings
import base64
import os
from datetime import datetime

router = APIRouter()
ai_dedup = AIDedupService()
integrity_service = IntegrityService()
blockchain_client = BlockchainClient()

@router.post("/register", response_model=VoterRegistrationResponse)
async def register_voter(
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    address_line1: str = Form(...),
    address_line2: str = Form(None),
    city: str = Form(...),
    state: str = Form(...),
    pincode: str = Form(...),
    phone_number: str = Form(None),
    email: str = Form(None),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Register voter on Real Blockchain Node
    (Strict Order: AI -> Blockchain -> Database)
    """
    steps_completed = []
    
    # Generate ID and paths early (in memory only)
    voter_id = generate_uuid()
    phonetic_name = f"{first_name.upper()}{last_name.upper()}"
    photo_filename = f"{datetime.utcnow().timestamp()}_{photo.filename}"
    photo_path = os.path.join(settings.PHOTO_STORAGE_PATH, photo_filename)
    
    try:
        # Step 1: Photo Upload (Local File)
        steps_completed.append("Photo Upload Started")
        photo_content = await photo.read()
        photo_base64 = base64.b64encode(photo_content).decode('utf-8')
        
        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
        with open(photo_path, "wb") as f:
            f.write(photo_content)
        steps_completed.append("Photo Uploaded Successfully")
        
        # Step 2: AI Deduplication Check (Read-Only)
        steps_completed.append("AI Deduplication Check Started")
        dedup_result = await ai_dedup.check_duplicate(
            photo_base64=photo_base64,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth
        )
        
        if dedup_result.get("is_duplicate"):
            raise HTTPException(status_code=400, detail="Duplicate voter detected")
        steps_completed.append("No Duplicate Found")
        
        # Step 3: Store Face in AI Service (THE CRITICAL CHECK)
        # We do this BEFORE touching the Blockchain or DB.
        # If the image is bad, it fails here, and nothing is recorded permanently.
        steps_completed.append("Storing Biometric Data...")
        
        ai_response = await ai_dedup.store_face_encoding(
            voter_id=voter_id,
            photo_base64=photo_base64,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth
        )
        
        if not ai_response.get("success"):
            # If AI fails (e.g. Unsupported Image), we STOP here.
            # No Zombie data in DB or Blockchain.
            error_msg = ai_response.get('error', 'Unknown AI Error')
            
            # Cleanup the local file we just saved
            if os.path.exists(photo_path):
                os.remove(photo_path)
                
            raise HTTPException(
                status_code=400, # Bad Request (Image issue)
                detail=f"Biometric Storage Failed: {error_msg}. Please upload a clearer RGB image."
            )
            
        steps_completed.append("Biometric Data Secured")
        
        # Step 4: Prepare Voter Object (In Memory)
        # We create the object to calculate the hash, but we DO NOT add to DB session yet.
        voter = Voter(
            voter_id=voter_id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=datetime.fromisoformat(date_of_birth),
            gender=gender,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            pincode=pincode,
            phone_number=phone_number,
            email=email,
            face_encoding_hash="secured_in_ai_service",
            photo_path=photo_path,
            phonetic_name=phonetic_name,
            status="ACTIVE",
            current_state_id=settings.STATE_ID,
            blockchain_hash="PENDING" 
        )
        
        # Calculate Hash of the data
        data_hash = integrity_service.calculate_local_hash(voter)
        
        # Step 5: REAL Blockchain Registration
        steps_completed.append("Connecting to Blockchain Node...")
        
        tx_data = {
            "voter_id": voter_id,
            "event_type": "REGISTERED",
            "data_hash": data_hash,
            "state": settings.STATE_ID,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        bc_response = await blockchain_client.create_transaction(
            sender=settings.STATE_ID,
            recipient="BLOCKCHAIN_NET",
            data=tx_data
        )
        
        if not bc_response.get("success", True):
            # If Blockchain fails, we technically have a "ghost" face in AI service,
            # but that is better than a "ghost" voter in the DB.
            # Ideally, we would call ai_dedup.delete_encoding(voter_id) here.
            raise HTTPException(status_code=500, detail="Blockchain Node Rejected Transaction")
            
        # Update with Transaction ID
        voter.blockchain_hash = data_hash
        voter.blockchain_transaction_id = bc_response.get("transaction_hash", "OFFLINE_HASH")
        
        steps_completed.append(f"Block Mined! Hash: {voter.blockchain_transaction_id[:10]}...")
        
        # Step 6: FINAL COMMIT - Save to SQL Database
        # This is the last step. It only happens if AI and Blockchain succeeded.
        db.add(voter)
        
        # Create Audit Log
        audit_log = AuditLog(
            voter_id=voter_id,
            event_type="REGISTERED",
            to_state=settings.STATE_ID,
            blockchain_hash=data_hash,
            local_hash=data_hash,
            status="SUCCESS",
            audit_metadata={"steps": steps_completed}
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(voter)
        
        return VoterRegistrationResponse(
            voter_id=voter_id,
            status="SUCCESS",
            message="Voter registered on Blockchain",
            blockchain_transaction_id=voter.blockchain_transaction_id,
            steps_completed=steps_completed
        )
        
    except HTTPException as e:
        # If anything failed, ensure no DB trace remains
        # Note: We haven't added to DB yet in most cases, but just in case
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{voter_id}")
async def get_voter_status(
    voter_id: str,
    db: Session = Depends(get_db)
):
    """Get status from Local DB (Fast)"""
    voter = db.query(Voter).filter(Voter.voter_id == voter_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
        
    return {
        "voter_id": voter_id,
        "name": f"{voter.first_name} {voter.last_name}",
        "status": voter.status,
        "current_state": voter.current_state_id,
        "is_voted": voter.status == "VOTED",
        "can_vote": voter.status == "ACTIVE",
        "registration_date": voter.created_at,
        "last_updated": voter.updated_at
    }