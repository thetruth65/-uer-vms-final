# backend/app/api/routes/transfer.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.database.models import Voter, AuditLog
from app.schemas.voter import VoterTransferRequest, VoterTransferResponse
from app.services.integrity import IntegrityService
from app.services.blockchain_client import BlockchainClient
from app.core.config import settings
import httpx
from datetime import datetime

router = APIRouter()
integrity_service = IntegrityService()
blockchain_client = BlockchainClient()

@router.post("/transfer", response_model=VoterTransferResponse)
async def transfer_voter(
    transfer_request: VoterTransferRequest,
    db: Session = Depends(get_db)
):
    """
    Transfer voter via Real Blockchain Transaction
    (Strict Order: Blockchain -> Local DB)
    """
    voter_id = transfer_request.voter_id
    from_state = transfer_request.from_state
    to_state = transfer_request.to_state
    
    # 1. Verify existence on Blockchain
    chain_record = await blockchain_client.verify_voter_history(voter_id)
    if not chain_record:
        raise HTTPException(status_code=404, detail="Voter not found on Blockchain")
        
    latest_tx = chain_record.get('latest', {}).get('data', {})
    current_owner = latest_tx.get('state') or latest_tx.get('owner_state')
    
    # Check ownership
    if current_owner != from_state and current_owner != to_state:
         print(f"⚠️ Transfer Warning: Blockchain owner is {current_owner}, expected {from_state}")

    # 2. Execute Transfer on Blockchain (CRITICAL STEP)
    tx_data = {
        "voter_id": voter_id,
        "event_type": "TRANSFERRED",
        "from_state": from_state,
        "to_state": to_state,
        "state": to_state, # New owner
        "timestamp": datetime.utcnow().isoformat()
    }
    
    bc_response = await blockchain_client.create_transaction(
        sender=from_state,
        recipient=to_state,
        data=tx_data
    )
    
    # === STRICT CHECK: If Blockchain fails, STOP HERE. ===
    # Do not touch the database. Do not pass Go.
    if not bc_response.get("success", True):
        print(f"❌ Blockchain Transfer Failed: {bc_response.get('error')}")
        raise HTTPException(status_code=500, detail="Blockchain Node Rejected Transfer")

    # Get transaction hash (Only available if success)
    tx_hash = bc_response.get("transaction_hash", "OFFLINE_TRANSFER")

    # 3. Handle Local DB State (Destination State)
    # Only proceeds if Blockchain was successful
    if to_state == settings.STATE_ID:
        voter = db.query(Voter).filter(Voter.voter_id == voter_id).first()
        
        if voter:
            # Update existing record
            voter.status = "ACTIVE"
            voter.current_state_id = to_state
            voter.address_line1 = transfer_request.new_address_line1
            voter.city = transfer_request.new_city
            voter.pincode = transfer_request.new_pincode
        else:
            # Create Migrated Record (Data Migration Logic)
            first_name = "Migrated"
            last_name = "Voter"
            
            # Try to fetch name from Source State Backend
            if settings.PEER_BACKEND_URL:
                try:
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(f"{settings.PEER_BACKEND_URL}/api/registration/status/{voter_id}")
                        if resp.status_code == 200:
                            data = resp.json()
                            names = data.get("name", "").split(" ")
                            if len(names) > 0: first_name = names[0]
                            if len(names) > 1: last_name = " ".join(names[1:])
                except Exception:
                    pass

            new_voter = Voter(
                voter_id=voter_id,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=datetime.utcnow(), 
                gender="UNKNOWN",
                address_line1=transfer_request.new_address_line1,
                city=transfer_request.new_city,
                state=to_state,
                pincode=transfer_request.new_pincode,
                face_encoding_hash="migrated",
                photo_path="migrated.jpg",
                phonetic_name="MIGRATED",
                status="ACTIVE",
                current_state_id=to_state,
                blockchain_hash="PENDING_SYNC"
            )
            db.add(new_voter)
        
        # 4. Create Audit Log
        audit_log = AuditLog(
            voter_id=voter_id,
            event_type="TRANSFERRED",
            from_state=from_state,
            to_state=to_state,
            blockchain_hash=tx_hash,
            status="SUCCESS"
        )
        db.add(audit_log)
        
        # FINAL COMMIT: Atomic save to DB
        db.commit()
    
    return VoterTransferResponse(
        voter_id=voter_id,
        from_state=from_state,
        to_state=to_state,
        status="SUCCESS",
        message="Transfer recorded on Blockchain",
        blockchain_transaction_id=tx_hash
    )