import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_cors import CORS
import numpy as np
import torch
import cv2
import logging
import base64
import json
import tempfile
from datetime import datetime
from config import API_HOST, API_PORT, SECRET_KEY, LOGS_DIR, IMG_SIZE, FEATURES_DIR, SILHOUETTES_DIR
from src.model import GaitCNN
from src.identify import identify_person, load_encrypted_db, cosine_similarity
from src.security import decrypt_feature
 
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["JWT_SECRET_KEY"] = SECRET_KEY
CORS(app)
jwt = JWTManager(app)
 
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "api.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
 
model = GaitCNN()
model.load_state_dict(torch.load("models/gait_model.pth", weights_only=True))
model.eval()
 
def log_action(action, details=""):
    msg = f"{action} | {details}"
    logging.info(msg)
    print(f"[LOG] {datetime.now()} | {msg}")
 
def extract_silhouette(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    _, binary = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resized = cv2.resize(binary, IMG_SIZE)
    return resized
 
def frame_to_base64(frame):
    _, buffer = cv2.imencode('.png', frame)
    return base64.b64encode(buffer).decode('utf-8')
 
@app.route("/")
def index():
    return render_template("index.html")
 
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data.get("username") == "admin" and data.get("password") == "admin123":
        token = create_access_token(identity="admin")
        log_action("LOGIN", "admin connecté")
        return jsonify({"token": token})
    return jsonify({"error": "Identifiants incorrects"}), 401
 
@app.route("/identify", methods=["POST"])
@jwt_required()
def identify():
    if "image" not in request.files:
        return jsonify({"error": "Aucune image fournie"}), 400
    file = request.files["image"]
    img_array = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, IMG_SIZE).astype(np.float32) / 255.0
    tensor = torch.tensor(img).unsqueeze(0).unsqueeze(0)
    with torch.no_grad():
        feat = model(tensor, return_features=True).numpy()[0]
    result = identify_person(feat)
    log_action("IDENTIFY", f"Résultat: {result}")
    return jsonify(result)
 
@app.route("/analyze-video", methods=["POST"])
def analyze_video():
    """
    Endpoint principal : prend une vidéo, extrait silhouettes,
    calcule features, compare avec toute la DB, retourne scores + silhouettes.
    """
    if "video" not in request.files:
        return jsonify({"error": "Aucune vidéo fournie"}), 400
 
    file = request.files["video"]
 
    # Sauvegarde temporaire
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name
        file.save(tmp_path)
 
    try:
        cap = cv2.VideoCapture(tmp_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 
        if total_frames == 0:
            return jsonify({"error": "Vidéo illisible"}), 400
 
        # Extrait 30 frames
        FRAMES = 30
        indices = np.linspace(0, total_frames - 1, FRAMES, dtype=int)
        silhouettes = []
        silhouette_b64 = []
        features_list = []
 
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            sil = extract_silhouette(frame)
            silhouettes.append(sil)
 
            # Base64 pour l'affichage (on envoie 10 max)
            if len(silhouette_b64) < 10:
                silhouette_b64.append(frame_to_base64(sil))
 
            # Feature extraction
            img_f = sil.astype(np.float32) / 255.0
            tensor = torch.tensor(img_f).unsqueeze(0).unsqueeze(0)
            with torch.no_grad():
                feat = model(tensor, return_features=True).numpy()[0]
            features_list.append(feat)
 
        cap.release()
 
        if len(features_list) == 0:
            return jsonify({"error": "Aucune frame extraite"}), 400
 
        # Vecteur moyen
        mean_feature = np.mean(features_list, axis=0)
 
        # Comparaison avec toute la DB
        db = load_encrypted_db()
        scores = {}
        for person_id, encrypted_vec in db.items():
            stored_vec = decrypt_feature(encrypted_vec)
            score = float(cosine_similarity(mean_feature, stored_vec))
            scores[person_id] = round(score, 4)
 
        # Identification finale
        result = identify_person(mean_feature)
 
        log_action("ANALYZE_VIDEO", f"Résultat: {result['person']} score={result['score']}")
 
        return jsonify({
            "result": result,
            "scores": scores,
            "silhouettes": silhouette_b64,
            "frames_analyzed": len(features_list)
        })
 
    finally:
        os.unlink(tmp_path)
 
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "GaitCNN", "persons": 5})
 
if __name__ == "__main__":
    log_action("STARTUP", "API démarrée")
    app.run(host=API_HOST, port=API_PORT, debug=False)
