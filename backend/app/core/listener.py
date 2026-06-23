import asyncio
import json
import logging
from sqlalchemy.orm import Session
from app.database.base import SessionLocal
from app.database.models import Voter, AuditLog
from app.core.config import settings
from app.core.events import pubsub_manager
from datetime import datetime

logger = logging.getLogger(__name__)

async def start_redis_listener():
    """Background task to listen for state-specific transfers"""
    if not pubsub_manager.redis_client:
        logger.warning("Redis not connected. Listener aborting.")
        return

    pubsub = pubsub_manager.redis_client.pubsub()
    channel_name = f"transfers_{settings.STATE_ID}"
    
    try:
        pubsub.subscribe(channel_name)
        logger.info(f"🎧 Listening for incoming transfers on Redis channel: {channel_name}")
        
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                try:
                    data = json.loads(message['data'])
                    if data.get("type") == "TRANSFER_INITIATED":
                        await handle_incoming_transfer(data)
                except Exception as e:
                    logger.error(f"Error processing Redis message: {e}")
                    
            await asyncio.sleep(1) # Prevent CPU pegging
            
    except Exception as e:
        logger.error(f"Redis Listener crashed: {e}")

async def handle_incoming_transfer(data: dict):
    voter_id = data.get("voter_id")
    from_state = data.get("from_state")
    to_state = data.get("to_state")
    blockchain_hash = data.get("blockchain_hash")
    
    if to_state != settings.STATE_ID:
        return # Not for us
        
    logger.info(f"🔄 Processing incoming transfer for {voter_id} from {from_state}")
    
    db: Session = SessionLocal()
    try:
        # Check if already exists
        voter = db.query(Voter).filter(Voter.voter_id == voter_id).first()
        if voter:
            voter.status = "ACTIVE"
            voter.current_state_id = to_state
            # Details would normally be fetched via an API call here, but for now we mark active
        else:
            # We create a placeholder. In a full system, State B queries State A via HTTP for full demographics.
            new_voter = Voter(
                voter_id=voter_id,
                first_name="Transferred",
                last_name="Voter",
                date_of_birth=datetime.utcnow(), 
                gender="UNKNOWN",
                address_line1="Pending Address Update",
                city="Pending",
                state=to_state,
                pincode="000000",
                face_encoding_hash="migrated",
                photo_path="migrated.jpg",
                phonetic_name="MIGRATED",
                status="ACTIVE",
                current_state_id=to_state,
                blockchain_hash="PENDING_SYNC"
            )
            db.add(new_voter)
            
        # Audit Log
        audit = AuditLog(
            voter_id=voter_id,
            event_type="TRANSFERRED_IN",
            from_state=from_state,
            to_state=to_state,
            blockchain_hash=blockchain_hash,
            status="SUCCESS"
        )
        db.add(audit)
        db.commit()
        logger.info(f"✅ Successfully processed transfer for {voter_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ DB Error saving transfer for {voter_id}: {e}")
    finally:
        db.close()
