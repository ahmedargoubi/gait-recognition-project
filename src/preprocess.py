import cv2
import numpy as np
import os
from config import RAW_VIDEOS_DIR, SILHOUETTES_DIR, FRAMES_PER_VIDEO, IMG_SIZE

def extract_silhouette(frame):
    """Convertit une frame en silhouette binaire"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    _, binary = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resized = cv2.resize(binary, IMG_SIZE)
    return resized

def process_video(video_path, person_id):
    """Extrait FRAMES_PER_VIDEO silhouettes d'une vidéo"""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        print(f"Erreur : impossible de lire {video_path}")
        return []

    # On prend des frames régulièrement espacées
    indices = np.linspace(0, total_frames - 1, FRAMES_PER_VIDEO, dtype=int)
    
    person_dir = os.path.join(SILHOUETTES_DIR, f"person_{person_id:02d}")
    os.makedirs(person_dir, exist_ok=True)
    
    saved = []
    for i, idx in enumerate(indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        silhouette = extract_silhouette(frame)
        path = os.path.join(person_dir, f"frame_{i:03d}.png")
        cv2.imwrite(path, silhouette)
        saved.append(path)
    
    cap.release()
    print(f"Person {person_id:02d} : {len(saved)} silhouettes extraites")
    return saved

def process_all_videos():
    """Traite toutes les vidéos du dossier raw_videos"""
    videos = sorted([
        f for f in os.listdir(RAW_VIDEOS_DIR) 
        if f.endswith('.mp4')
    ])
    
    if len(videos) == 0:
        print("Aucune vidéo trouvée dans data/raw_videos/")
        return
    
    print(f"{len(videos)} vidéos trouvées. Extraction en cours...")
    
    for i, video_file in enumerate(videos, start=1):
        video_path = os.path.join(RAW_VIDEOS_DIR, video_file)
        process_video(video_path, person_id=i)
    
    print("Extraction terminée !")

if __name__ == "__main__":
    process_all_videos()