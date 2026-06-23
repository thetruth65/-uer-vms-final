import numpy as np
from typing import List, Dict, Optional
import os
from datetime import datetime
from app.core.config import settings
import logging
import base64
import cv2
from deepface import DeepFace
from app.database import SessionLocal, FaceEncoding

# Configure logger
logger = logging.getLogger("uvicorn.error")

class FaceRecognitionService:
    def __init__(self):
        self.threshold = settings.FACE_MATCH_THRESHOLD
        
        # Pre-download the model weights on startup to avoid delay during first request
        logger.info("🔧 Loading DeepFace Model (FaceNet512)...")
        try:
            # This triggers the weight download
            DeepFace.build_model("Facenet512")
            logger.info("✅ DeepFace Model Loaded")
        except Exception as e:
            logger.warning(f"⚠️ Model load deferred: {e}")
    
    def extract_encoding(self, photo_input: str) -> Optional[np.ndarray]:
        """
        Extract face encoding using DeepFace (FaceNet512)
        """
        try:
            # 1. Decode Base64 to Bytes
            if isinstance(photo_input, str):
                if "base64," in photo_input:
                    photo_input = photo_input.split("base64,")[1]
                image_bytes = base64.b64decode(photo_input)
            else:
                image_bytes = photo_input

            # 2. Convert Bytes to Numpy Array (BGR for OpenCV)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                logger.error("❌ OpenCV failed to decode image")
                return None

            # 3. Generate Embedding using DeepFace
            logger.info("🧠 Running DeepFace representation...")
            
            embedding_objs = DeepFace.represent(
                img_path=img,
                model_name="Facenet512",
                detector_backend="opencv", # Lightweight backend
                enforce_detection=True,
                align=True
            )
            
            if not embedding_objs:
                return None
                
            # Take the first face found
            embedding = embedding_objs[0]["embedding"]
            logger.info(f"✅ Generated 512-dim embedding")
            
            return np.array(embedding)

        except ValueError as ve:
            logger.warning(f"⚠️ Face detection failed: {str(ve)}")
            return None
        except Exception as e:
            logger.error(f"❌ Critical Error in DeepFace: {str(e)}")
            return None
    
    def find_matching_face(self, face_encoding: np.ndarray) -> Optional[Dict]:
        """
        O(log N) Search using Approximate Nearest Neighbor (ANN) via pgvector
        """
        try:
            # Normalize input vector for Cosine Similarity
            source_norm = face_encoding / np.linalg.norm(face_encoding)
            source_list = source_norm.tolist()
        except Exception:
            return None
            
        with SessionLocal() as db:
            # Query for the closest face using pgvector's cosine distance operator `<=>`
            closest_match = db.query(FaceEncoding).order_by(
                FaceEncoding.embedding.cosine_distance(source_list)
            ).first()
            
            if closest_match:
                # Calculate actual distance
                distance = db.query(
                    FaceEncoding.embedding.cosine_distance(source_list)
                ).filter(FaceEncoding.voter_id == closest_match.voter_id).scalar()
                
                if distance is not None and distance < self.threshold:
                    return {
                        'voter_id': closest_match.voter_id,
                        'distance': float(distance),
                        'confidence': float(1 - distance),
                        'metadata': closest_match.metadata_json
                    }
        return None
    
    def store_encoding(self, voter_id: str, face_encoding: np.ndarray, metadata: Dict):
        # Normalize stored vector
        target_norm = face_encoding / np.linalg.norm(face_encoding)
        target_list = target_norm.tolist()
        
        with SessionLocal() as db:
            # Check if exists
            existing = db.query(FaceEncoding).filter(FaceEncoding.voter_id == voter_id).first()
            if existing:
                existing.embedding = target_list
                existing.metadata_json = {**metadata, 'stored_at': datetime.utcnow().isoformat()}
            else:
                new_encoding = FaceEncoding(
                    voter_id=voter_id,
                    embedding=target_list,
                    metadata_json={**metadata, 'stored_at': datetime.utcnow().isoformat()}
                )
                db.add(new_encoding)
            
            db.commit()
            logger.info(f"💾 Saved DeepFace encoding to PostgreSQL (pgvector) for {voter_id}")

    def get_total_encodings(self):
        with SessionLocal() as db:
            return db.query(FaceEncoding).count()

    def delete_encoding(self, voter_id: str):
        with SessionLocal() as db:
            db.query(FaceEncoding).filter(FaceEncoding.voter_id == voter_id).delete()
            db.commit()
            logger.info(f"🗑️ Deleted DeepFace encoding for {voter_id}")