# backend/app/api/routes/voting.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.database.models import Voter, AuditLog
from app.schemas.voter import VoteResponse
from app.services.ai_dedup import AIDedupService
from app.services.blockchain_client import BlockchainClient
from app.services.integrity import IntegrityService
from app.core.config import settings
from datetime import datetime
import base64

router = APIRouter()
ai_dedup = AIDedupService()
blockchain_client = BlockchainClient()
integrity_service = IntegrityService() 

@router.get("/eligibility/{voter_id}")
async def check_voting_eligibility(
    voter_id: str,
    db: Session = Depends(get_db)
):
    """Check if voter is eligible to vote (With Bi-Directional Sync)"""
    
    # 1. Local Check
    voter = db.query(Voter).filter(Voter.voter_id == voter_id).first()
    
    if not voter:
        return {"eligible": False, "reason": "Voter not found locally"}

    # 2. Blockchain Check
    chain_history = await blockchain_client.verify_voter_history(voter_id)
    if not chain_history:
        return {"eligible": False, "reason": "Voter not found on Blockchain"}

    latest_tx = chain_history.get('latest', {}).get('data', {})
    chain_owner = latest_tx.get('state') or latest_tx.get('owner_state') or latest_tx.get('to_state')
    event_type = latest_tx.get('event_type') or latest_tx.get('event')

    # 3. SELF-HEALING SYNC
    if chain_owner:
        # Case A: Blockchain says they belong elsewhere (User Left)
        if chain_owner != settings.STATE_ID:
            if voter.status == "ACTIVE":
                print(f"🔄 SYNC: Voter moved to {chain_owner}. Updating local DB.")
                voter.status = "MOVED"
                voter.current_state_id = chain_owner
                db.commit()
            return {"eligible": False, "reason": f"Voter has moved to {chain_owner}"}
        
        # Case B: Blockchain says they belong HERE (User Returned or never left)
        elif chain_owner == settings.STATE_ID:
            if voter.status == "MOVED":
                print(f"🔄 SYNC: Blockchain confirms ownership. Restoring ACTIVE status.")
                voter.status = "ACTIVE"
                voter.current_state_id = settings.STATE_ID
                db.commit()

    # 4. Check Voted Status
    if event_type == "VOTED":
        return {"eligible": False, "reason": "Already voted on Blockchain"}
    
    # 5. Final Status Check
    if voter.status != "ACTIVE":
        return {"eligible": False, "reason": f"Voter status is {voter.status}"}
    
    return {
        "eligible": True,
        "voter_id": voter_id,
        "name": f"{voter.first_name} {voter.last_name}",
        "state": voter.current_state_id
    }

@router.post("/vote", response_model=VoteResponse)
async def cast_vote(
    voter_id: str = Form(...),
    polling_booth_id: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    print(f"🗳️ Voting Process Started for {voter_id}")

    # 1. Verify Local
    voter = db.query(Voter).filter(Voter.voter_id == voter_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
        
    # Auto-Heal Check (Just in case eligibility wasn't called)
    if voter.status == "MOVED":
        # Quick check to see if we should actually be ACTIVE
        chain_history = await blockchain_client.verify_voter_history(voter_id)
        if chain_history:
            latest = chain_history.get('latest', {}).get('data', {})
            owner = latest.get('state') or latest.get('owner_state')
            if owner == settings.STATE_ID:
                print("🔄 Auto-Healing status to ACTIVE before voting")
                voter.status = "ACTIVE"
                db.commit()

    if voter.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Voter status is {voter.status}")

    # 2. Biometric Check
    photo_content = await photo.read()
    photo_base64 = base64.b64encode(photo_content).decode('utf-8')
    
    print(f"🕵️ Checking Biometrics...")
    
    dedup_result = await ai_dedup.check_duplicate(
        photo_base64=photo_base64,
        first_name=voter.first_name,
        last_name=voter.last_name,
        date_of_birth=str(voter.date_of_birth)
    )
    
    matched_id = dedup_result.get("matched_voter_id")
    details = dedup_result.get("details", {})
    face_conf = details.get("face_confidence", 0)
    
    print(f"🕵️ AI RESULT: Matched={matched_id}, FaceConf={face_conf}")
    
    is_valid = False
    # LENIENT CHECK: ID matches AND confidence > 0.15
    if matched_id == voter_id and face_conf > 0.15:
        is_valid = True
        
    if not is_valid:
        raise HTTPException(status_code=401, detail="Biometric Verification Failed")

    # 3. Check Blockchain for Double Vote
    history = await blockchain_client.verify_voter_history(voter_id)
    if history:
        last = history.get('latest', {}).get('data', {})
        if last.get('event_type') == "VOTED":
            raise HTTPException(status_code=400, detail="Double voting prevented: Already voted on Blockchain")

    # 4. Prepare Transaction
    current_data_hash = integrity_service.calculate_local_hash(voter)
    
    tx_data = {
        "voter_id": voter_id,
        "event_type": "VOTED",
        "data_hash": current_data_hash, 
        "polling_booth": polling_booth_id,
        "state": settings.STATE_ID,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # 5. Send to Blockchain
    print("🔗 Sending Vote to Blockchain...")
    bc_response = await blockchain_client.create_transaction(
        sender=settings.STATE_ID,
        recipient="BLOCKCHAIN_NET",
        data=tx_data
    )
    
    # 🛑 CRITICAL CHECK: If this fails, code stops here. DB NOT UPDATED.
    if not bc_response.get("success", True):
        print(f"❌ Blockchain Vote Failed: {bc_response.get('error')}")
        raise HTTPException(status_code=500, detail="Blockchain Transaction Failed")

    # 6. Commit to Local DB (Only reached if Step 5 succeeds)
    print("✅ Blockchain Success. Updating Local DB...")
    tx_hash = bc_response.get("transaction_hash", "PENDING")
    
    voter.status = "VOTED"
    voter.last_voted_at = datetime.utcnow()
    voter.voter_metadata = {"voted_tx": tx_hash}
    
    # Audit Log
    audit_log = AuditLog(
        voter_id=voter_id,
        event_type="VOTED",
        to_state=settings.STATE_ID,
        blockchain_hash=tx_hash,
        status="SUCCESS"
    )
    db.add(audit_log)
    db.commit()
    
    return VoteResponse(
        voter_id=voter_id,
        status="SUCCESS",
        message="Vote Recorded",
        blockchain_transaction_id=tx_hash,
        voted_at=datetime.utcnow()
    )