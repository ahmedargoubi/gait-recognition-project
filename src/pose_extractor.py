import cv2
import numpy as np
import os
import sys
import urllib.request
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FRAMES_PER_VIDEO

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision as mp_vision

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pose_landmarker.task"
)

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Téléchargement du modèle MediaPipe...")
        url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
        urllib.request.urlretrieve(url, MODEL_PATH)
        print(f"Modèle sauvegardé : {MODEL_PATH}")

def calc_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

KEY_IDS = [23, 24, 25, 26, 27, 28, 11, 12, 13, 14]

def landmarks_to_feature(lm):
    """
    Vecteur 100% invariant à l'angle de caméra :
    - Angles articulaires (indépendants de la position dans l'image)
    - Ratios de distances (indépendants de la taille dans l'image)
    - Symétrie gauche/droite (style de marche unique)
    Total : 20 valeurs par frame
    """

    def pt(i):
        return np.array([lm[i].x, lm[i].y])

    def angle(a, b, c):
        return calc_angle(pt(a).tolist(), pt(b).tolist(), pt(c).tolist()) / 180.0

    def dist(i, j):
        return float(np.linalg.norm(pt(i) - pt(j)) + 1e-8)

    # ── 10 ANGLES ARTICULAIRES ──
    angles = [
        angle(23, 25, 27),   # genou gauche
        angle(24, 26, 28),   # genou droit
        angle(11, 23, 25),   # hanche gauche
        angle(12, 24, 26),   # hanche droite
        angle(11, 13, 15),   # coude gauche
        angle(12, 14, 16),   # coude droit
        angle(23, 11, 13),   # épaule gauche
        angle(24, 12, 14),   # épaule droite
        angle(25, 27, 31),   # cheville gauche
        angle(26, 28, 32),   # cheville droite
    ]

    # ── 6 RATIOS DE DISTANCES (normalisés par hauteur du corps) ──
    hauteur_corps = dist(11, 27) + dist(12, 28)  # épaule → genou normalisé
    hauteur_corps = max(hauteur_corps, 1e-6)

    ratios = [
        dist(27, 28) / hauteur_corps,  # écart chevilles
        dist(25, 26) / hauteur_corps,  # écart genoux
        dist(23, 24) / hauteur_corps,  # écart hanches
        dist(11, 12) / hauteur_corps,  # écart épaules
        dist(11, 23) / (dist(23, 25) + 1e-8),  # ratio torse/cuisse gauche
        dist(12, 24) / (dist(24, 26) + 1e-8),  # ratio torse/cuisse droit
    ]

    # ── 4 ASYMÉTRIES GAUCHE/DROITE (signature unique de chaque personne) ──
    asymetries = [
        angle(23, 25, 27) - angle(24, 26, 28),   # diff genou G-D
        angle(11, 23, 25) - angle(12, 24, 26),   # diff hanche G-D
        dist(11, 27) / (dist(12, 28) + 1e-8),   # ratio longueur jambe G/D
        dist(13, 15) / (dist(14, 16) + 1e-8),   # ratio longueur bras G/D
    ]

    feature = angles + ratios + asymetries  # 20 valeurs
    return np.array(feature, dtype=np.float32)

def extract_pose_sequence(video_path):
    download_model()

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        cap.release()
        return None

    indices = np.linspace(0, total_frames - 1, FRAMES_PER_VIDEO, dtype=int)
    sequence = []

    base_opts = python.BaseOptions(model_asset_path=MODEL_PATH)
    opts = mp_vision.PoseLandmarkerOptions(
        base_options=base_opts,
        running_mode=mp_vision.RunningMode.IMAGE
    )

    with mp_vision.PoseLandmarker.create_from_options(opts) as landmarker:
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if not ret:
                sequence.append(np.zeros(20, dtype=np.float32))
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            result = landmarker.detect(mp_image)

            if not result.pose_landmarks or len(result.pose_landmarks) == 0:
                sequence.append(np.zeros(20, dtype=np.float32))
            else:
                lm = result.pose_landmarks[0]
                sequence.append(landmarks_to_feature(lm))

    cap.release()

    sequence = np.array(sequence)  # (30, 20)
    return sequence.flatten()       # (600,)


if __name__ == "__main__":
    from config import RAW_VIDEOS_DIR
    videos = [f for f in os.listdir(RAW_VIDEOS_DIR) if f.endswith('.mp4')]
    if not videos:
        print("Aucune vidéo trouvée dans data/raw_videos/")
    else:
        path = os.path.join(RAW_VIDEOS_DIR, videos[0])
        print(f"Test sur : {videos[0]}")
        feat = extract_pose_sequence(path)
        if feat is not None:
            print(f"OK — shape: {feat.shape}")
            print(f"Valeurs non-nulles : {np.count_nonzero(feat)}/780")
        else:
            print("Echec")