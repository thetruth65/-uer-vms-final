import jellyfish
from datetime import datetime
from typing import Dict

class SimilarityService:
    @staticmethod
    def phonetic_match(name1: str, name2: str) -> float:
        """
        Compare names using phonetic algorithm (Soundex)
        Returns: similarity score 0-1
        """
        # Clean names
        name1 = name1.upper().strip()
        name2 = name2.upper().strip()
        
        # Exact match
        if name1 == name2:
            return 1.0
        
        # Soundex phonetic matching
        soundex1 = jellyfish.soundex(name1)
        soundex2 = jellyfish.soundex(name2)
        
        if soundex1 == soundex2:
            return 0.9
        
        # Levenshtein distance
        max_len = max(len(name1), len(name2))
        if max_len == 0:
            return 0.0
        
        distance = jellyfish.levenshtein_distance(name1, name2)
        similarity = 1.0 - (distance / max_len)
        
        return similarity
    
    @staticmethod
    def date_match(dob1: str, dob2: str) -> bool:
        """
        Compare dates of birth
        Returns: True if exact match
        """
        try:
            date1 = datetime.fromisoformat(dob1).date()
            date2 = datetime.fromisoformat(dob2).date()
            return date1 == date2
        except:
            return False
    
    @staticmethod
    def calculate_combined_score(
        face_match: Dict,
        name_similarity: float,
        dob_match: bool
    ) -> Dict:
        """
        Calculate combined matching score using multiple factors
        """
        scores = []
        weights = []
        
        # Face matching (highest weight)
        if face_match:
            scores.append(face_match['confidence'])
            weights.append(0.6)
        
        # Name similarity
        scores.append(name_similarity)
        weights.append(0.25)
        
        # DOB match (binary)
        scores.append(1.0 if dob_match else 0.0)
        weights.append(0.15)
        
        # Weighted average
        total_weight = sum(weights)
        combined_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        # Determine match type
        match_types = []
        if face_match and face_match['confidence'] > 0.7:
            match_types.append("FACE")
        if name_similarity > 0.8:
            match_types.append("NAME")
        if dob_match:
            match_types.append("DOB")
        
        match_type = "+".join(match_types) if match_types else "NONE"
        
        return {
            'combined_score': combined_score,
            'face_confidence': face_match['confidence'] if face_match else 0.0,
            'name_similarity': name_similarity,
            'dob_match': dob_match,
            'match_type': match_type,
            'is_duplicate': combined_score > 0.75  # Threshold for duplicate
        }