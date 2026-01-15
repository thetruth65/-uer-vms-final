# backend/app/services/integrity.py
import hashlib
import json
from app.services.blockchain_client import BlockchainClient

class IntegrityService:
    def __init__(self):
        self.blockchain = BlockchainClient()

    def calculate_local_hash(self, voter_data) -> str:
        """Create SHA-256 hash of critical sensitive fields."""
        canonical_data = {
            "voter_id": voter_data.voter_id,
            "name": f"{voter_data.first_name} {voter_data.last_name}",
            "dob": voter_data.date_of_birth.isoformat() if hasattr(voter_data.date_of_birth, 'isoformat') else str(voter_data.date_of_birth),
            "state": voter_data.current_state_id,
            "address": voter_data.address_line1
        }
        data_str = json.dumps(canonical_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    async def verify_voter_integrity(self, voter_sql_record):
        local_hash = self.calculate_local_hash(voter_sql_record)
        
        # 1. Check Metadata for Simulation Flag
        # If we purposely hacked it, we mark it specifically
        meta = voter_sql_record.voter_metadata or {}
        is_simulated = meta.get("hacked", False)

        chain_record = await self.blockchain.verify_voter_history(voter_sql_record.voter_id)
        
        # 2. Check Service Failure / Missing on Chain
        if not chain_record:
            return {
                "status": "SERVICE_FAILED", 
                "details": "Blockchain Service Unreachable or Record Missing",
                "local_hash": local_hash,
                "chain_hash": "UNKNOWN"
            }
            
        latest_tx = chain_record.get('latest', {})
        chain_hash = latest_tx.get('data', {}).get('data_hash')
        
        # 3. Check for Mismatch
        if local_hash == chain_hash:
            return {
                "status": "SECURE", 
                "details": "Blockchain signature verified",
                "local_hash": local_hash,
                "chain_hash": chain_hash
            }
        else:
            # Hash Mismatch! Is it our simulation or a real attack?
            status_label = "SIMULATED_TAMPERING" if is_simulated else "TAMPERED"
            return {
                "status": status_label, 
                "details": "CRITICAL: Database hash does not match Blockchain hash!",
                "local_hash": local_hash,
                "chain_hash": chain_hash
            }