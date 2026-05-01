import os
import base64
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ENCRYPTION_KEY_FILE
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def generate_key():
    """Génère et sauvegarde une clé AES-256"""
    key = os.urandom(32)
    with open(ENCRYPTION_KEY_FILE, "wb") as f:
        f.write(key)
    print("Clé AES-256 générée.")
    return key

def load_key():
    """Charge la clé existante ou en génère une nouvelle"""
    if os.path.exists(ENCRYPTION_KEY_FILE):
        with open(ENCRYPTION_KEY_FILE, "rb") as f:
            return f.read()
    return generate_key()

def encrypt_feature(feature_vector: np.ndarray) -> str:
    """Chiffre un vecteur numpy en AES-256-GCM"""
    key = load_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    data = feature_vector.astype(np.float32).tobytes()
    encrypted = aesgcm.encrypt(nonce, data, None)
    result = base64.b64encode(nonce + encrypted).decode("utf-8")
    return result

def decrypt_feature(encrypted_str: str, feature_dim: int = 128) -> np.ndarray:
    """Déchiffre un vecteur numpy"""
    key = load_key()
    aesgcm = AESGCM(key)
    raw = base64.b64decode(encrypted_str.encode("utf-8"))
    nonce = raw[:12]
    encrypted = raw[12:]
    data = aesgcm.decrypt(nonce, encrypted, None)
    return np.frombuffer(data, dtype=np.float32)

def encrypt_all_features():
    """Chiffre tous les fichiers .npy dans data/features/"""
    from config import FEATURES_DIR
    files = [f for f in os.listdir(FEATURES_DIR) if f.endswith(".npy")]
    encrypted_db = {}
    for fname in files:
        person_id = fname.replace(".npy", "")
        vec = np.load(os.path.join(FEATURES_DIR, fname))
        encrypted_db[person_id] = encrypt_feature(vec)
        print(f"{person_id} chiffré (AES-256-GCM)")
    import json
    with open(os.path.join(FEATURES_DIR, "encrypted_db.json"), "w") as f:
        json.dump(encrypted_db, f)
    print("Base biométrique chiffrée sauvegardée.")
    return encrypted_db

if __name__ == "__main__":
    encrypt_all_features()