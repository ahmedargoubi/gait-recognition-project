import os

# Chemins principaux
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_VIDEOS_DIR = os.path.join(DATA_DIR, "raw_videos")
SILHOUETTES_DIR = os.path.join(DATA_DIR, "silhouettes")
FEATURES_DIR = os.path.join(DATA_DIR, "features")

# Paramètres IA
IMG_SIZE = (64, 64)        # taille des silhouettes
FEATURE_DIM = 128          # taille du vecteur d'identification
NUM_PERSONS = 5            # nombre de personnes dans le dataset
FRAMES_PER_VIDEO = 30      # nombre de frames extraites par vidéo

# Paramètres sécurité
SECRET_KEY = "gait_secret_key_2024"   # clé JWT (à changer en prod)
ENCRYPTION_KEY_FILE = os.path.join(BASE_DIR, "encryption.key")

# Paramètres API
API_HOST = "127.0.0.1"
API_PORT = 5000

# Logs
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(SILHOUETTES_DIR, exist_ok=True)
os.makedirs(FEATURES_DIR, exist_ok=True)