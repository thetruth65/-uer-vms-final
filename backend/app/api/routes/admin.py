# backend/app/api/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.base import get_db
from app.database.models import Voter, AuditLog
from app.services.integrity import IntegrityService
from typing import List
from app.services.blockchain_client import BlockchainClient # Import this


router = APIRouter()
integrity_service = IntegrityService()
blockchain_client = BlockchainClient() # Initialize


# --- PRIVACY HELPERS ---
def mask_phone(phone: str):
    if not phone or len(phone) < 4: return "N/A"
    return f"{phone[:2]}******{phone[-2:]}"

def mask_dob(dob):
    return "**-**-****"

@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """Get dashboard statistics (Anonymized)"""
    
    total_voters = db.query(func.count(Voter.voter_id)).scalar()
    active_voters = db.query(func.count(Voter.voter_id)).filter(Voter.status == "ACTIVE").scalar()
    voted_voters = db.query(func.count(Voter.voter_id)).filter(Voter.status == "VOTED").scalar()
    
    # We fetch blocks from the Real Blockchain Service ideally, 
    # but for dashboard speed, we can use a local counter or fetch from service
    # For now, returning DB stats
    
    recent_registrations = db.query(Voter).order_by(Voter.created_at.desc()).limit(5).all()
    
    return {
        "total_voters": total_voters,
        "active_voters": active_voters,
        "voted_voters": voted_voters,
        "total_blockchain_blocks": total_voters + voted_voters, # Approx count for demo
        "recent_registrations": [
            {
                "voter_id": v.voter_id,
                "name": f"{v.first_name} {v.last_name[0]}.", # Privacy: First Name + Last Initial
                "registered_at": v.created_at
            }
            for v in recent_registrations
        ],
        "recent_blockchain_events": [] # Populated by Frontend via Blockchain Service API
    }

@router.post("/run-integrity-check")
async def run_integrity_check(
    db: Session = Depends(get_db)
):
    """
    REAL TIME AUDIT:
    Scans local SQL Database and verifies hashes against the Real Blockchain Service.
    Returns list of voters with status (SECURE vs TAMPERED).
    """
    voters = db.query(Voter).all()
    report = []
    
    for voter in voters:
        # Verify against the separate Blockchain Node
        result = await integrity_service.verify_voter_integrity(voter)
        
        report.append({
            "voter_id": voter.voter_id,
            "name": f"{voter.first_name} {voter.last_name}", # Full name visible only to Admin
            "status": result["status"],
            "details": result["details"],
            "hash_mismatch": result.get("status") == "TAMPERED"
        })
        
    return report

@router.post("/simulate-hack/{voter_id}")
async def simulate_hack(
    voter_id: str, 
    db: Session = Depends(get_db)
):
    """
    DEMO TOOL: Manually alters SQL data WITHOUT updating Blockchain.
    This creates a 'Tampered' state to show the judges.
    """
    voter = db.query(Voter).filter(Voter.voter_id == voter_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    # The Hack: Maliciously change address in SQL only
    original_address = voter.address_line1
    voter.address_line1 = "HACKED ADDRESS #999"
    
    # We deliberately DO NOT update the blockchain_hash column or call the blockchain
    # This ensures the hashes will mismatch in the Integrity Check
    voter.voter_metadata = {"hacked": True, "original_address": original_address}
    
    db.commit()
    
    return {
        "message": f"⚠️ SYSTEM COMPROMISED: Voter {voter_id} address changed locally. Blockchain remains immutable.",
        "blockchain_status": "Unchanged"
    }


# [NEW] Restore this endpoint so Frontend doesn't crash
@router.get("/blockchain/explorer")
async def blockchain_explorer():
    """
    Proxy request to Real Blockchain Service and format for Frontend
    """
    raw_chain_data = await blockchain_client.get_full_chain()
    chain = raw_chain_data.get("chain", [])
    
    formatted_blocks = []
    
    # Convert Real Blockchain format to Frontend Table format
    for block in chain:
        # Transactions is a list, we just grab the first one for the summary view
        txs = block.get("transactions", [])
        tx_data = txs[0].get("data", {}) if txs else {}
        
        formatted_blocks.append({
            "block_number": block.get("index"),
            "transaction_id": block.get("previous_hash")[:15], # Using hash as ID for display
            "voter_id": tx_data.get("voter_id", "System/Genesis"),
            "event_type": tx_data.get("event_type", "MINED"),
            "owner_state": tx_data.get("state", "Network"),
            "data_hash": tx_data.get("data_hash", "N/A"),
            "timestamp": str(block.get("timestamp"))
        })
    
    # Sort by latest first
    formatted_blocks.reverse()
    
    return {
        "total_blocks": len(chain),
        "blocks": formatted_blocks
    }