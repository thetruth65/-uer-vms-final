# backend/app/services/hash_service.py
import hashlib
import json
from datetime import datetime

class HashService:
    @staticmethod
    def generate_voter_hash(voter_data: dict) -> str:
        """Generate SHA-256 hash of voter record"""
        # Sort keys to ensure consistent hashing
        sorted_data = json.dumps(voter_data, sort_keys=True, default=str)
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    @staticmethod
    def generate_transaction_id(voter_id: str, event_type: str) -> str:
        """Generate unique transaction ID"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{voter_id}:{event_type}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def verify_hash(data: dict, expected_hash: str) -> bool:
        """Verify data hash matches expected hash"""
        calculated_hash = HashService.generate_voter_hash(data)
        return calculated_hash == expected_hash