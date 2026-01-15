# ai-service/app/models/face_recognition.py
import face_recognition
import numpy as np
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from app.core.config import settings
import logging
import base64
from PIL import Image
import io

# Configure logger
logger = logging.getLogger("uvicorn.error")

class FaceRecognitionService:
    def __init__(self):
        self.storage_path = settings.STORAGE_PATH
        self.encodings_file = os.path.join(self.storage_path, "face_encodings.json")
        self.threshold = settings.FACE_MATCH_THRESHOLD
        
        logger.info(f"🔧 Initializing FaceRecognitionService")
        logger.info(f"   └─ Storage: {self.storage_path}")
        logger.info(f"   └─ Threshold: {self.threshold}")
        
        # Check for incompatible numpy version
        np_version = np.__version__
        logger.info(f"   └─ NumPy version: {np_version}")
        if np_version.startswith('2.'):
            error_msg = f"❌ Detected incompatible numpy version {np_version}. This causes 'Unsupported image type' errors in face_recognition/dlib."
            error_msg += "\n   └─ Please downgrade numpy to 1.26.4: pip install numpy==1.26.4 --force-reinstall"
            error_msg += "\n   └─ If using virtual env, recreate it and install compatible versions."
            logger.error(error_msg)
            raise ValueError("Incompatible numpy version. Downgrade to 1.26.4 to use face_recognition.")
        
        os.makedirs(self.storage_path, exist_ok=True)
        self.encodings_db = self._load_encodings()
        logger.info(f"   ✅ Loaded {len(self.encodings_db)} existing face encodings")
    
    def _load_encodings(self) -> Dict:
        """Load face encodings from JSON file"""
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, 'r') as f:
                    data = json.load(f)
                # Convert lists back to numpy arrays
                for voter_id in data:
                    data[voter_id]['encoding'] = np.array(data[voter_id]['encoding'])
                logger.info(f"✅ Loaded {len(data)} encodings from file")
                return data
            except Exception as e:
                logger.error(f"❌ Error loading encodings: {str(e)}")
                return {}
        return {}
    
    def _save_encodings(self):
        """Save face encodings to JSON file"""
        try:
            save_data = {}
            for voter_id, data in self.encodings_db.items():
                save_data[voter_id] = {
                    'encoding': data['encoding'].tolist(),
                    'metadata': data['metadata']
                }
            
            with open(self.encodings_file, 'w') as f:
                json.dump(save_data, f)
            logger.info(f"💾 Saved {len(save_data)} encodings to file")
        except Exception as e:
            logger.error(f"❌ Error saving encodings: {str(e)}")
    
    def extract_encoding(self, photo_input: str) -> Optional[np.ndarray]:
        """
        Extract face encoding from image - BULLETPROOF VERSION
        
        Args:
            photo_input: Base64 encoded image string
            
        Returns:
            128-dimensional face encoding array or None if failed
        """
        logger.info("🔷 Starting face encoding extraction")
        
        try:
            # Step 1: Decode base64
            logger.info("   📝 Step 1: Decoding base64...")
            if isinstance(photo_input, str):
                if "base64," in photo_input:
                    photo_input = photo_input.split("base64,")[1]
                image_bytes = base64.b64decode(photo_input)
                logger.info(f"      ✓ Decoded {len(image_bytes)} bytes")
            else:
                image_bytes = photo_input
                logger.info(f"      ✓ Using raw bytes: {len(image_bytes)} bytes")

            # Step 2: Load with PIL
            logger.info("   🖼️  Step 2: Loading image with PIL...")
            try:
                image_pil = Image.open(io.BytesIO(image_bytes))
                logger.info(f"      ✓ PIL loaded: mode={image_pil.mode}, size={image_pil.size}")
            except Exception as e:
                logger.error(f"      ❌ PIL failed: {str(e)}")
                return None

            # Step 3: Convert to RGB and ensure 8-bit
            logger.info("   🎨 Step 3: Converting to RGB...")
            if image_pil.mode != 'RGB':
                logger.info(f"      └─ Converting {image_pil.mode} → RGB")
                image_pil = image_pil.convert('RGB')
            logger.info("      ✓ Image is RGB")

            # Handle potential RGBA or other modes more robustly
            if image_pil.mode == 'RGBA':
                image_pil = image_pil.convert('RGB')
                logger.info("      └─ Converted RGBA to RGB")

            # Ensure it's 8-bit by quantizing if necessary
            if image_pil.mode == 'P':
                image_pil = image_pil.convert('RGB')
            # If it's float or 16-bit, convert to 8-bit
            image_pil = image_pil.convert('RGB')  # Redundant but safe

            # Step 4: Convert to numpy with PROPER memory layout
            logger.info("   🔢 Step 4: Creating numpy array...")
            
            # Create a properly formatted array from PIL
            img_array = np.asarray(image_pil)
            
            # If not uint8, convert to uint8
            if img_array.dtype != np.uint8:
                logger.info(f"      └─ Converting dtype {img_array.dtype} to uint8")
                if np.issubdtype(img_array.dtype, np.floating):
                    img_array = (img_array * 255).astype(np.uint8)
                else:
                    img_array = img_array.astype(np.uint8)
            
            # CRITICAL: Create a NEW array with proper C-order memory layout
            img_array = np.array(img_array, dtype=np.uint8, order='C')
            
            logger.info(f"      ✓ Array created: shape={img_array.shape}, dtype={img_array.dtype}")
            logger.info(f"      └─ C-contiguous: {img_array.flags['C_CONTIGUOUS']}")
            logger.info(f"      └─ Writeable: {img_array.flags['WRITEABLE']}")
            logger.info(f"      └─ Owns data: {img_array.flags['OWNDATA']}")
            
            # Double check array properties
            if img_array.ndim != 3:
                logger.error(f"      ❌ Wrong dimensions: {img_array.ndim} (expected 3)")
                return None
            
            if img_array.shape[2] != 3:
                logger.error(f"      ❌ Wrong channels: {img_array.shape[2]} (expected 3)")
                return None
            
            # Step 5: EMERGENCY WORKAROUND - Save and reload with face_recognition
            logger.info("   💾 Step 5: Using disk-based workaround...")
            temp_path = os.path.join(self.storage_path, "temp_face_check.jpg")
            
            try:
                # Save PIL image to disk as JPEG to force 8-bit RGB
                image_pil.save(temp_path, format='JPEG', quality=95)
                logger.info(f"      └─ Saved temp file: {temp_path}")
                
                # Load with face_recognition's built-in loader (guaranteed compatible)
                img_array = face_recognition.load_image_file(temp_path)
                logger.info(f"      ✓ Reloaded with face_recognition loader")
                logger.info(f"      └─ Shape: {img_array.shape}, dtype: {img_array.dtype}")
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.info("      ✓ Temp file removed")
                    
            except Exception as e:
                logger.error(f"      ❌ Disk workaround failed: {str(e)}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return None
            
            # ADDITIONAL FIX: Ensure the array is contiguous in memory and uint8
            img_array = np.ascontiguousarray(img_array.astype(np.uint8))
            logger.info(f"      └─ Forced contiguous: C={img_array.flags['C_CONTIGUOUS']}, dtype={img_array.dtype}")

            # Step 6: Detect faces (should work now!)
            logger.info("   🔍 Step 6: Detecting faces...")
            
            try:
                face_locations = face_recognition.face_locations(img_array, model="hog")
            except RuntimeError as e:
                logger.error(f"      ❌ Still failed: {str(e)}")
                logger.error("         └─ This is often caused by numpy version >=2.0. Please downgrade to 1.26.4")
                logger.error("         └─ Check your numpy version: import numpy; print(numpy.__version__)")
                return None
            
            if not face_locations:
                logger.warning("      ⚠️  No faces detected")
                return None
            
            logger.info(f"      ✓ Found {len(face_locations)} face(s)")
            logger.info(f"      └─ Location: {face_locations[0]}")
            
            # Step 7: Generate encoding
            logger.info("   🧬 Step 7: Generating encoding...")
            
            try:
                encodings = face_recognition.face_encodings(img_array, face_locations)
            except Exception as e:
                logger.error(f"      ❌ Encoding failed: {str(e)}")
                return None
            
            if not encodings:
                logger.warning("      ⚠️  No encodings generated")
                return None
            
            encoding = encodings[0]
            logger.info(f"      ✅ Encoding generated (128-dim)")
            logger.info(f"      └─ Sample: [{encoding[0]:.4f}, {encoding[1]:.4f}, ...]")
            
            return encoding
            
        except Exception as e:
            logger.error(f"   ❌ CRITICAL ERROR:")
            logger.error(f"      └─ {str(e)}")
            logger.error(f"      └─ Type: {type(e).__name__}")
            import traceback
            logger.error(f"      └─ Trace: {traceback.format_exc()}")
            return None
    
    def find_matching_face(self, face_encoding: np.ndarray) -> Optional[Dict]:
        """Search for matching face"""
        logger.info(f"🔍 Searching {len(self.encodings_db)} encodings")
        
        if not len(self.encodings_db):
            logger.info("   └─ Database empty")
            return None
        
        best_match = None
        best_distance = float('inf')
        
        for voter_id, data in self.encodings_db.items():
            stored_encoding = data['encoding']
            distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
            
            logger.debug(f"   └─ {voter_id}: {distance:.4f}")
            
            if distance < best_distance and distance < self.threshold:
                best_distance = distance
                best_match = {
                    'voter_id': voter_id,
                    'distance': float(distance),
                    'confidence': 1.0 - distance,
                    'metadata': data['metadata']
                }
        
        if best_match:
            logger.info(f"   ✅ MATCH: {best_match['voter_id']} ({best_match['confidence']:.2%})")
        else:
            logger.info(f"   ❌ No match (threshold: {self.threshold})")
        
        return best_match
    
    def store_encoding(self, voter_id: str, face_encoding: np.ndarray, metadata: Dict):
        """Store encoding"""
        logger.info(f"💾 Storing: {voter_id}")
        
        self.encodings_db[voter_id] = {
            'encoding': face_encoding,
            'metadata': {**metadata, 'stored_at': datetime.utcnow().isoformat()}
        }
        
        self._save_encodings()
        logger.info(f"   ✅ Stored (total: {len(self.encodings_db)})")