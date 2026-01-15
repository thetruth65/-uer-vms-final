# backend/app/schemas/voter.py
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, date
from typing import Optional, List
import re

class VoterRegistrationRequest(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip()
    
    @validator('pincode')
    def validate_pincode(cls, v):
        if not re.match(r'^\d{6}$', v):
            raise ValueError('Pincode must be 6 digits')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        if v.upper() not in ['MALE', 'FEMALE', 'OTHER']:
            raise ValueError('Gender must be MALE, FEMALE, or OTHER')
        return v.upper()

class VoterRegistrationResponse(BaseModel):
    voter_id: str
    status: str
    message: str
    blockchain_transaction_id: str
    steps_completed: List[str]
    
    class Config:
        from_attributes = True

class VoterTransferRequest(BaseModel):
    voter_id: str
    from_state: str
    to_state: str
    new_address_line1: str
    new_address_line2: Optional[str] = None
    new_city: str
    new_pincode: str

class VoterTransferResponse(BaseModel):
    voter_id: str
    from_state: str
    to_state: str
    status: str
    message: str
    blockchain_transaction_id: str
    
    class Config:
        from_attributes = True

class VoteRequest(BaseModel):
    voter_id: str
    polling_booth_id: str

class VoteResponse(BaseModel):
    voter_id: str
    status: str
    message: str
    blockchain_transaction_id: str
    voted_at: datetime
    
    class Config:
        from_attributes = True

class VoterStatusResponse(BaseModel):
    voter_id: str
    status: str
    current_state: str
    is_voted: bool
    can_vote: bool
    registration_date: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True