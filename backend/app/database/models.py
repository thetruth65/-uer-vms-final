from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, JSON
from sqlalchemy.sql import func
from app.database.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Voter(Base):
    __tablename__ = "voters"
    
    voter_id = Column(String(50), primary_key=True, default=generate_uuid)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(20), nullable=False)
    
    # Address
    address_line1 = Column(String(200), nullable=False)
    address_line2 = Column(String(200))
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    
    # Contact
    phone_number = Column(String(15))
    email = Column(String(100))
    
    # Biometric (Hashed)
    face_encoding_hash = Column(Text, nullable=False)
    photo_path = Column(String(500), nullable=False)
    phonetic_name = Column(String(100), nullable=False)
    
    # Status
    status = Column(String(20), default="ACTIVE")
    current_state_id = Column(String(50), nullable=False)
    
    # Blockchain Reference
    blockchain_hash = Column(String(64), nullable=False)
    blockchain_transaction_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_voted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata - RENAMED to avoid SQLAlchemy conflict
    voter_metadata = Column(JSON, default={})

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    voter_id = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)
    from_state = Column(String(50))
    to_state = Column(String(50))
    blockchain_hash = Column(String(64))
    local_hash = Column(String(64))
    status = Column(String(20), default="SUCCESS")
    error_message = Column(Text)
    audit_metadata = Column(JSON, default={})  # RENAMED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BlockchainLedger(Base):
    __tablename__ = "blockchain_ledger"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    block_number = Column(Integer, nullable=False)
    transaction_id = Column(String(100), unique=True, nullable=False)
    voter_id = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)
    
    # Asset Ownership
    owner_state_id = Column(String(50), nullable=False)
    previous_owner_state_id = Column(String(50))
    
    # Data Integrity
    data_hash = Column(String(64), nullable=False)
    previous_hash = Column(String(64))
    current_hash = Column(String(64), nullable=False)
    
    # Consensus
    consensus_nodes = Column(JSON, default=[])
    confirmed = Column(Boolean, default=True)
    
    # Metadata - RENAMED
    block_metadata = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class VoterAsset(Base):
    __tablename__ = "voter_assets"
    
    voter_id = Column(String(50), primary_key=True)
    current_owner_state = Column(String(50), nullable=False)
    status = Column(String(20), default="ACTIVE")
    data_hash = Column(String(64), nullable=False)
    
    # Registration
    registration_transaction_id = Column(String(100))
    registration_timestamp = Column(DateTime(timezone=True))
    
    # Latest Transaction
    latest_transaction_id = Column(String(100))
    latest_event = Column(String(50))
    
    # Voting Lock
    is_voted = Column(Boolean, default=False)
    voted_transaction_id = Column(String(100))
    voted_timestamp = Column(DateTime(timezone=True))
    
    # Transfer History
    transfer_history = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())