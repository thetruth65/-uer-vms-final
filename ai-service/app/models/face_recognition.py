import numpy as np
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from app.core.config import settings
import logging
import base64
import cv2
from deepface import DeepFace

# Configure logger
logger = logging.getLogger("uvicorn.error")

class FaceRecognitionService:
    def __init__(self):
        self.storage_path = settings.STORAGE_PATH
        self.encodings_file = os.path.join(self.storage_path, "face_encodings.json")
        
        # DeepFace Cosine Threshold for Facenet512 is typically 0.4
        # We use the setting from config, but note that scale is different now.
        # Dlib (Euclidean) < 0.6. DeepFace (Cosine) < 0.4.
        self.threshold = 0.4 
        # === NEW LOGGING ===
        abs_path = os.path.abspath(self.encodings_file)
        logger.info(f"📂 LOADING ENCODINGS FROM: {abs_path}")
        # ===================
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Pre-download the model weights on startup to avoid delay during first request
        logger.info("🔧 Loading DeepFace Model (FaceNet512)...")
        try:
            # This triggers the weight download
            DeepFace.build_model("Facenet512")
            logger.info("✅ DeepFace Model Loaded")
        except Exception as e:
            logger.warning(f"⚠️ Model load deferred: {e}")

        self.encodings_db = self._load_encodings()
    
    def _load_encodings(self) -> Dict:
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, 'r') as f:
                    data = json.load(f)
                for voter_id in data:
                    data[voter_id]['encoding'] = np.array(data[voter_id]['encoding'])
                return data
            except Exception:
                return {}
        return {}
    
    def _save_encodings(self):
        save_data = {}
        for voter_id, data in self.encodings_db.items():
            save_data[voter_id] = {
                'encoding': data['encoding'].tolist(),
                'metadata': data['metadata']
            }
        with open(self.encodings_file, 'w') as f:
            json.dump(save_data, f)
    
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
            # enforce_detection=False allows it to run even if face is blurry (returns risk, but less crashes)
            # But for voting, we want enforce_detection=True to ensure a face exists.
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
            # DeepFace raises ValueError if "Face could not be detected" when enforce_detection=True
            logger.warning(f"⚠️ Face detection failed: {str(ve)}")
            return None
        except Exception as e:
            logger.error(f"❌ Critical Error in DeepFace: {str(e)}")
            return None
    
    def find_matching_face(self, face_encoding: np.ndarray) -> Optional[Dict]:
        """
        1:N Search using Cosine Distance
        """
        if not len(self.encodings_db):
            return None
        
        best_match = None
        best_distance = float('inf')
        
        # Normalize input vector for Cosine Similarity
        try:
            source_norm = face_encoding / np.linalg.norm(face_encoding)
        except Exception:
            return None
        
        for voter_id, data in self.encodings_db.items():
            stored_vec = np.array(data['encoding'])
            
            # --- CRITICAL FIX: Skip incompatible vectors ---
            if stored_vec.shape != face_encoding.shape:
                logger.warning(f"⚠️ Skipping {voter_id}: Dimension mismatch ({stored_vec.shape} vs {face_encoding.shape})")
                continue
            # -----------------------------------------------
            
            # Normalize stored vector
            target_norm = stored_vec / np.linalg.norm(stored_vec)
            
            # Cosine Distance = 1 - Cosine Similarity
            cosine_similarity = np.dot(source_norm, target_norm)
            distance = 1 - cosine_similarity
            
            # logger.info(f"   👉 {voter_id}: Dist={distance:.4f} (Thresh: {self.threshold})")
            
            if distance < best_distance and distance < self.threshold:
                best_distance = distance
                best_match = {
                    'voter_id': voter_id,
                    'distance': float(distance),
                    'confidence': float(cosine_similarity),
                    'metadata': data['metadata']
                }
        
        return best_match
    
    def store_encoding(self, voter_id: str, face_encoding: np.ndarray, metadata: Dict):
        self.encodings_db[voter_id] = {
            'encoding': face_encoding,
            'metadata': {**metadata, 'stored_at': datetime.utcnow().isoformat()}
        }
        self._save_encodings()
        logger.info(f"💾 Saved DeepFace encoding for {voter_id}")