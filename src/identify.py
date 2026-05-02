import numpy as np
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FEATURES_DIR
from src.security import decrypt_feature

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

def load_encrypted_db():
    db_path = os.path.join(FEATURES_DIR, "encrypted_db.json")
    with open(db_path, "r") as f:
        return json.load(f)

def identify_person(query_feature: np.ndarray, threshold: float = 0.30):
    """Identifie une personne par similarité cosinus"""
    db = load_encrypted_db()
    best_match = None
    best_score = -1

    for person_id, encrypted_vec in db.items():
        stored_vec = decrypt_feature(encrypted_vec)
        score = cosine_similarity(query_feature, stored_vec)
        if score > best_score:
            best_score = score
            best_match = person_id

    if best_score >= threshold:
        return {"status": "identified", "person": best_match, "score": round(float(best_score), 4)}
    else:
        return {"status": "unknown", "person": None, "score": round(float(best_score), 4)}

if __name__ == "__main__":
    # Test avec person_01
    test_vec = np.load(os.path.join(FEATURES_DIR, "person_01.npy"))
    result = identify_person(test_vec)
    print(f"Résultat identification : {result}")