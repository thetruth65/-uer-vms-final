# backend/app/services/ai_dedup.py
import httpx
import base64
from typing import Optional, Dict
from app.core.config import settings

class AIDedupService:
    def __init__(self):
        self.ai_service_url = settings.AI_SERVICE_URL
    
    async def check_duplicate(
        self, 
        photo_base64: str, 
        first_name: str, 
        last_name: str, 
        date_of_birth: str
    ) -> Dict:
        """
        Check if voter already exists using AI deduplication
        Returns: {
            "is_duplicate": bool,
            "matched_voter_id": str or None,
            "confidence_score": float,
            "match_type": str (FACE, NAME, DOB, MULTIPLE)
        }
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ai_service_url}/api/dedup/check",
                    json={
                        "photo_base64": photo_base64,
                        "first_name": first_name,
                        "last_name": last_name,
                        "date_of_birth": date_of_birth
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "is_duplicate": False,
                        "error": "AI service unavailable"
                    }
        except Exception as e:
            print(f"AI Dedup Error: {str(e)}")
            return {
                "is_duplicate": False,
                "error": str(e)
            }
    
    async def store_face_encoding(
        self, 
        voter_id: str, 
        photo_base64: str, 
        first_name: str, 
        last_name: str, 
        date_of_birth: str
    ) -> Dict:
        """Store face encoding for future comparisons"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ai_service_url}/api/dedup/store",
                    json={
                        "voter_id": voter_id,
                        "photo_base64": photo_base64,
                        "first_name": first_name,
                        "last_name": last_name,
                        "date_of_birth": date_of_birth
                    }
                )
                
                return response.json()
        except Exception as e:
            print(f"Store encoding error: {str(e)}")
            return {"success": False, "error": str(e)}