# backend/app/blockchain/smart_contract.py
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Optional
import uuid
import logging
from app.database.models import BlockchainLedger, VoterAsset
from app.services.hash_service import HashService

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SmartContract:
    def __init__(self, blockchain_db: Session):
        self.blockchain_db = blockchain_db
        self.hash_service = HashService()
        logger.info("SmartContract initialized")
    
    def register_voter(
        self, 
        voter_id: str, 
        data_hash: str, 
        state_id: str
    ) -> Dict:
        """
        Register a new voter on the blockchain
        Creates a voter asset owned by the registering state
        """
        logger.info(f"🔵 BLOCKCHAIN: Starting voter registration for {voter_id}")
        logger.info(f"   └─ State: {state_id}, Data Hash: {data_hash[:16]}...")
        
        try:
            # Generate transaction ID
            transaction_id = self.hash_service.generate_transaction_id(voter_id, "REGISTERED")
            logger.info(f"   ✓ Transaction ID generated: {transaction_id[:16]}...")
            
            # Get block details
            block_number = self._get_next_block_number()
            logger.info(f"   ✓ Block number: {block_number}")
            
            previous_hash = self._get_latest_hash()
            logger.info(f"   ✓ Previous hash: {previous_hash[:16]}...")
            
            # Generate current hash
            current_hash = self.hash_service.generate_voter_hash({
                "block_number": block_number,
                "transaction_id": transaction_id,
                "voter_id": voter_id,
                "event_type": "REGISTERED",
                "data_hash": data_hash,
                "previous_hash": previous_hash
            })
            logger.info(f"   ✓ Current hash generated: {current_hash[:16]}...")
            
            # Create blockchain ledger entry
            logger.info(f"   🔷 Creating BlockchainLedger entry...")
            ledger_entry = BlockchainLedger(
                block_number=block_number,
                transaction_id=transaction_id,
                voter_id=voter_id,
                event_type="REGISTERED",
                owner_state_id=state_id,
                data_hash=data_hash,
                previous_hash=previous_hash,
                current_hash=current_hash,
                consensus_nodes=[state_id],
                confirmed=True,
                block_metadata={"registration_state": state_id}
            )
            logger.info(f"   ✓ BlockchainLedger object created")
            
            # Create voter asset
            logger.info(f"   🔷 Creating VoterAsset entry...")
            voter_asset = VoterAsset(
                voter_id=voter_id,
                current_owner_state=state_id,
                status="ACTIVE",
                data_hash=data_hash,
                registration_transaction_id=transaction_id,
                registration_timestamp=datetime.utcnow(),
                latest_transaction_id=transaction_id,
                latest_event="REGISTERED",
                transfer_history=[]
            )
            logger.info(f"   ✓ VoterAsset object created")
            
            # Add to session
            logger.info(f"   💾 Adding entries to database session...")
            self.blockchain_db.add(ledger_entry)
            logger.info(f"   ✓ BlockchainLedger added to session")
            
            self.blockchain_db.add(voter_asset)
            logger.info(f"   ✓ VoterAsset added to session")
            
            # Flush to ensure no constraint violations before commit
            logger.info(f"   💾 Flushing session...")
            self.blockchain_db.flush()
            logger.info(f"   ✓ Session flushed successfully")
            
            # Commit transaction
            logger.info(f"   💾 Committing transaction...")
            self.blockchain_db.commit()
            logger.info(f"   ✅ BLOCKCHAIN: Registration committed successfully!")
            
            # Verify voter asset was created
            logger.info(f"   🔍 Verifying VoterAsset creation...")
            verification = self.blockchain_db.query(VoterAsset).filter(
                VoterAsset.voter_id == voter_id
            ).first()
            
            if verification:
                logger.info(f"   ✅ VoterAsset verified in database: {verification.voter_id}")
            else:
                logger.error(f"   ❌ VoterAsset NOT found after commit! voter_id={voter_id}")
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "block_number": block_number,
                "voter_id": voter_id,
                "owner_state": state_id
            }
            
        except Exception as e:
            logger.error(f"   ❌ BLOCKCHAIN ERROR during registration: {str(e)}")
            logger.error(f"   └─ Error type: {type(e).__name__}")
            logger.error(f"   └─ Rolling back transaction...")
            self.blockchain_db.rollback()
            raise
    
    def transfer_voter(
        self, 
        voter_id: str, 
        from_state: str, 
        to_state: str, 
        new_data_hash: str
    ) -> Dict:
        """
        Transfer voter ownership from one state to another
        Implements smart contract logic for ownership transfer
        """
        logger.info(f"🔵 BLOCKCHAIN: Starting voter transfer for {voter_id}")
        logger.info(f"   └─ From: {from_state} → To: {to_state}")
        
        try:
            # Verify current ownership
            logger.info(f"   🔍 Verifying voter ownership...")
            voter_asset = self.blockchain_db.query(VoterAsset).filter(
                VoterAsset.voter_id == voter_id
            ).first()
            
            if not voter_asset:
                logger.error(f"   ❌ Voter asset not found: {voter_id}")
                return {"success": False, "error": "Voter not found"}
            
            logger.info(f"   ✓ Voter found: current_owner={voter_asset.current_owner_state}")
            
            if voter_asset.current_owner_state != from_state:
                logger.error(f"   ❌ Ownership mismatch: expected {from_state}, got {voter_asset.current_owner_state}")
                return {"success": False, "error": "Ownership verification failed"}
            
            logger.info(f"   ✓ Ownership verified")
            
            if voter_asset.is_voted:
                logger.error(f"   ❌ Cannot transfer: voter has already voted")
                return {"success": False, "error": "Cannot transfer: voter has already voted"}
            
            logger.info(f"   ✓ Vote status: not voted, transfer allowed")
            
            # Execute transfer
            transaction_id = self.hash_service.generate_transaction_id(voter_id, "TRANSFERRED")
            logger.info(f"   ✓ Transaction ID: {transaction_id[:16]}...")
            
            block_number = self._get_next_block_number()
            previous_hash = self._get_latest_hash()
            current_hash = self.hash_service.generate_voter_hash({
                "block_number": block_number,
                "transaction_id": transaction_id,
                "voter_id": voter_id,
                "event_type": "TRANSFERRED",
                "from_state": from_state,
                "to_state": to_state,
                "previous_hash": previous_hash
            })
            
            logger.info(f"   🔷 Creating transfer ledger entry (Block #{block_number})...")
            ledger_entry = BlockchainLedger(
                block_number=block_number,
                transaction_id=transaction_id,
                voter_id=voter_id,
                event_type="TRANSFERRED",
                owner_state_id=to_state,
                previous_owner_state_id=from_state,
                data_hash=new_data_hash,
                previous_hash=previous_hash,
                current_hash=current_hash,
                consensus_nodes=[from_state, to_state],
                confirmed=True,
                block_metadata={
                    "from_state": from_state,
                    "to_state": to_state,
                    "transfer_reason": "RELOCATION"
                }
            )
            logger.info(f"   ✓ Ledger entry created")
            
            # Update voter asset
            logger.info(f"   🔷 Updating VoterAsset ownership...")
            voter_asset.current_owner_state = to_state
            voter_asset.data_hash = new_data_hash
            voter_asset.latest_transaction_id = transaction_id
            voter_asset.latest_event = "TRANSFERRED"
            logger.info(f"   ✓ Ownership updated: {from_state} → {to_state}")
            
            # Add to transfer history
            transfer_history = voter_asset.transfer_history or []
            transfer_history.append({
                "from_state": from_state,
                "to_state": to_state,
                "transaction_id": transaction_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            voter_asset.transfer_history = transfer_history
            logger.info(f"   ✓ Transfer history updated (total transfers: {len(transfer_history)})")
            
            # Commit
            logger.info(f"   💾 Committing transfer transaction...")
            self.blockchain_db.add(ledger_entry)
            self.blockchain_db.flush()
            self.blockchain_db.commit()
            logger.info(f"   ✅ BLOCKCHAIN: Transfer committed successfully!")
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "block_number": block_number,
                "voter_id": voter_id,
                "from_state": from_state,
                "to_state": to_state
            }
            
        except Exception as e:
            logger.error(f"   ❌ BLOCKCHAIN ERROR during transfer: {str(e)}")
            logger.error(f"   └─ Error type: {type(e).__name__}")
            logger.error(f"   └─ Rolling back transaction...")
            self.blockchain_db.rollback()
            raise
    
    def mark_voted(self, voter_id: str, polling_booth_id: str) -> Dict:
        """
        Mark voter as voted and lock the voter asset
        Prevents double voting nationwide
        """
        logger.info(f"🔵 BLOCKCHAIN: Marking voter as VOTED: {voter_id}")
        logger.info(f"   └─ Polling Booth: {polling_booth_id}")
        
        try:
            # Find voter asset
            logger.info(f"   🔍 Looking up voter asset...")
            voter_asset = self.blockchain_db.query(VoterAsset).filter(
                VoterAsset.voter_id == voter_id
            ).first()
            
            if not voter_asset:
                logger.error(f"   ❌ Voter asset not found: {voter_id}")
                return {"success": False, "error": "Voter not found"}
            
            logger.info(f"   ✓ Voter found: status={voter_asset.status}, is_voted={voter_asset.is_voted}")
            
            if voter_asset.is_voted:
                logger.error(f"   ❌ Double voting attempt prevented!")
                logger.error(f"   └─ Already voted at: {voter_asset.voted_timestamp}")
                return {
                    "success": False, 
                    "error": "Double voting prevented: voter has already voted",
                    "voted_at": voter_asset.voted_timestamp
                }
            
            logger.info(f"   ✓ Voter has not voted yet, proceeding with vote lock...")
            
            # Generate transaction
            transaction_id = self.hash_service.generate_transaction_id(voter_id, "VOTED")
            logger.info(f"   ✓ Transaction ID: {transaction_id[:16]}...")
            
            block_number = self._get_next_block_number()
            previous_hash = self._get_latest_hash()
            current_hash = self.hash_service.generate_voter_hash({
                "block_number": block_number,
                "transaction_id": transaction_id,
                "voter_id": voter_id,
                "event_type": "VOTED",
                "previous_hash": previous_hash
            })
            
            logger.info(f"   🔷 Creating VOTED ledger entry (Block #{block_number})...")
            ledger_entry = BlockchainLedger(
                block_number=block_number,
                transaction_id=transaction_id,
                voter_id=voter_id,
                event_type="VOTED",
                owner_state_id=voter_asset.current_owner_state,
                data_hash=voter_asset.data_hash,
                previous_hash=previous_hash,
                current_hash=current_hash,
                consensus_nodes=[voter_asset.current_owner_state],
                confirmed=True,
                block_metadata={"polling_booth_id": polling_booth_id}
            )
            logger.info(f"   ✓ Ledger entry created")
            
            # Lock asset
            logger.info(f"   🔒 Locking voter asset (nationwide lock)...")
            voter_asset.is_voted = True
            voter_asset.status = "VOTED"
            voter_asset.voted_transaction_id = transaction_id
            voter_asset.voted_timestamp = datetime.utcnow()
            voter_asset.latest_transaction_id = transaction_id
            voter_asset.latest_event = "VOTED"
            logger.info(f"   ✓ Voter asset locked")
            
            # Commit
            logger.info(f"   💾 Committing vote transaction...")
            self.blockchain_db.add(ledger_entry)
            self.blockchain_db.flush()
            self.blockchain_db.commit()
            logger.info(f"   ✅ BLOCKCHAIN: Vote recorded and locked successfully!")
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "block_number": block_number,
                "voter_id": voter_id,
                "voted_at": voter_asset.voted_timestamp
            }
            
        except Exception as e:
            logger.error(f"   ❌ BLOCKCHAIN ERROR during voting: {str(e)}")
            logger.error(f"   └─ Error type: {type(e).__name__}")
            logger.error(f"   └─ Rolling back transaction...")
            self.blockchain_db.rollback()
            raise
    
    def _get_next_block_number(self) -> int:
        """Get the next block number"""
        latest_block = self.blockchain_db.query(BlockchainLedger).order_by(
            BlockchainLedger.block_number.desc()
        ).first()
        next_block = (latest_block.block_number + 1) if latest_block else 1
        logger.debug(f"   📊 Next block number: {next_block}")
        return next_block
    
    def _get_latest_hash(self) -> Optional[str]:
        """Get the hash of the latest block"""
        latest_block = self.blockchain_db.query(BlockchainLedger).order_by(
            BlockchainLedger.block_number.desc()
        ).first()
        latest_hash = latest_block.current_hash if latest_block else "0" * 64
        logger.debug(f"   📊 Latest hash: {latest_hash[:16]}...")
        return latest_hash