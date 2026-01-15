# ai-service/app/api/routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models.face_recognition import FaceRecognitionService
from app.models.similarity import SimilarityService

router = APIRouter()
face_service = FaceRecognitionService()
similarity_service = SimilarityService()

class DedupCheckRequest(BaseModel):
    photo_base64: str
    first_name: str
    last_name: str
    date_of_birth: str

class DedupCheckResponse(BaseModel):
    is_duplicate: bool
    matched_voter_id: Optional[str] = None
    confidence_score: float
    match_type: str
    details: dict

class StoreEncodingRequest(BaseModel):
    voter_id: str
    photo_base64: str
    first_name: str
    last_name: str
    date_of_birth: str

@router.post("/dedup/check", response_model=DedupCheckResponse)
async def check_duplicate(request: DedupCheckRequest):
    """
    Check if voter is a duplicate using multi-factor matching
    """
    
    # Step 1: Extract face encoding
    face_encoding = face_service.extract_encoding(request.photo_base64)
    
    if face_encoding is None:
        # If no face found, we can't do biometric check
        return DedupCheckResponse(
            is_duplicate=False,
            matched_voter_id=None,
            confidence_score=0.0,
            match_type="NO_FACE",
            details={'message': 'No face detected'}
        )
    
    # Step 2: Search for matching face
    face_match = face_service.find_matching_face(face_encoding)
    
    # Step 3: Calculate name similarity
    full_name = f"{request.first_name} {request.last_name}"
    
    # If face match found, compare with that voter's name
    if face_match:
        matched_name = face_match['metadata'].get('name', '')
        name_similarity = similarity_service.phonetic_match(full_name, matched_name)
        
        # Compare DOB
        matched_dob = face_match['metadata'].get('date_of_birth', '')
        dob_match = similarity_service.date_match(request.date_of_birth, matched_dob)
        
        # Calculate combined score
        result = similarity_service.calculate_combined_score(
            face_match=face_match,
            name_similarity=name_similarity,
            dob_match=dob_match
        )
        
        # === THE FIX IS HERE ===
        # Even if "Combined Score" is low (due to name mismatch), 
        # if the Face Confidence is high (> 0.6), we MUST return the ID 
        # so the Voting Backend can verify it.
        
        strong_face_match = face_match['confidence'] > 0.6
        
        if result['is_duplicate'] or strong_face_match:
            return DedupCheckResponse(
                is_duplicate=result['is_duplicate'], # Keep original logic for dedup
                matched_voter_id=face_match['voter_id'], # ALWAYS return ID if face matches
                confidence_score=result['combined_score'],
                match_type=result['match_type'],
                details={
                    'face_distance': face_match['distance'],
                    'face_confidence': face_match['confidence'], # Explicitly send this
                    'name_similarity': result['name_similarity'],
                    'dob_match': result['dob_match']
                }
            )
    
    # No match found
    return DedupCheckResponse(
        is_duplicate=False,
        matched_voter_id=None,
        confidence_score=0.0,
        match_type="NONE",
        details={
            'faces_searched': len(face_service.encodings_db),
            'message': 'No duplicate found'
        }
    )

@router.post("/dedup/store")
async def store_face_encoding(request: StoreEncodingRequest):
    """
    Store face encoding for future comparisons
    """
    
    # Extract face encoding
    face_encoding = face_service.extract_encoding(request.photo_base64)
    
    if face_encoding is None:
        raise HTTPException(
            status_code=400, 
            detail="No face detected in photo"
        )
    
    # Store encoding with metadata
    metadata = {
        'name': f"{request.first_name} {request.last_name}",
        'date_of_birth': request.date_of_birth
    }
    
    face_service.store_encoding(
        voter_id=request.voter_id,
        face_encoding=face_encoding,
        metadata=metadata
    )
    
    return {
        "success": True,
        "voter_id": request.voter_id,
        "message": "Face encoding stored successfully",
        "total_encodings": len(face_service.encodings_db)
    }

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Deduplication Service",
        "total_face_encodings": len(face_service.encodings_db)
    }