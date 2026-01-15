# backend/app/scripts/seed_mock_data.py
"""Seed database with mock data"""
import json
import sys
from sqlalchemy.orm import Session
from app.database.base import SessionLocal, BlockchainSessionLocal
from app.database.models import Voter
from app.blockchain.smart_contract import SmartContract
from app.services.hash_service import HashService
from datetime import datetime
import random

def seed_mock_data():
    """Seed database with mock voters"""
    db = SessionLocal()
    blockchain_db = BlockchainSessionLocal()
    hash_service = HashService()
    smart_contract = SmartContract(blockchain_db)
    
    try:
        # Load mock data
        with open('/app/mock-data/voters.json', 'r') as f:
            voters_data = json.load(f)
        
        print(f"📥 Loaded {len(voters_data)} mock voters")
        
        for idx, voter_data in enumerate(voters_data[:10]):  # Seed first 10
            # Generate voter ID
            voter_id = f"VOTER_{str(idx+1).zfill(5)}"
            
            # Create voter record
            voter = Voter(
                voter_id=voter_id,
                first_name=voter_data['first_name'],
                last_name=voter_data['last_name'],
                date_of_birth=datetime.fromisoformat(voter_data['date_of_birth']),
                gender=voter_data['gender'],
                address_line1=voter_data['address_line1'],
                address_line2=voter_data.get('address_line2'),
                city=voter_data['city'],
                state=voter_data['state'],
                pincode=voter_data['pincode'],
                phone_number=voter_data.get('phone_number'),
                email=voter_data.get('email'),
                face_encoding_hash=f"hash_{voter_id}",
                photo_path=f"/storage/photos/mock_{voter_id}.jpg",
                phonetic_name=f"{voter_data['first_name']}{voter_data['last_name']}".upper(),
                status="ACTIVE",
                current_state_id="STATE_A",
                blockchain_hash=hash_service.generate_voter_hash(voter_data)
            )
            
            db.add(voter)
            db.commit()
            
            # Register on blockchain
            blockchain_result = smart_contract.register_voter(
                voter_id=voter_id,
                data_hash=voter.blockchain_hash,
                state_id="STATE_A"
            )
            
            # Update with transaction ID
            voter.blockchain_transaction_id = blockchain_result['transaction_id']
            db.commit()
            
            print(f"✅ Seeded voter {idx+1}: {voter.first_name} {voter.last_name}")
        
        print(f"\n🎉 Successfully seeded {idx+1} voters!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {str(e)}")
        db.rollback()
        blockchain_db.rollback()
    finally:
        db.close()
        blockchain_db.close()

if __name__ == "__main__":
    seed_mock_data()