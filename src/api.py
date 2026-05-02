import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_cors import CORS
import numpy as np
import torch
import cv2
import logging
import base64
import tempfile
from datetime import datetime

from config import API_HOST, API_PORT, SECRET_KEY, LOGS_DIR, IMG_SIZE, FEATURES_DIR
from src.model_pose import GaitPoseCNN
from src.pose_extractor import extract_pose_sequence
from src.identify import identify_person, load_encrypted_db, cosine_similarity
from src.security import decrypt_feature

app = Flask(__name__,
            template_folder=os.path.join(ROOT, 'templates'),
            static_folder=os.path.join(ROOT, 'static'))
app.config["JWT_SECRET_KEY"] = SECRET_KEY
CORS(app)
jwt = JWTManager(app)

logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "api.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

MODEL_PATH = os.path.join(ROOT, "models", "gait_pose_model.pth")
model = GaitPoseCNN()
model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
model.eval()

def log_action(action, details=""):
    msg = f"{action} | {details}"
    logging.info(msg)
    print(f"[LOG] {datetime.now()} | {msg}")

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

@app.route("/analyze-video", methods=["POST"])
def analyze_video():
    if "video" not in request.files:
        return jsonify({"error": "Aucune vidéo fournie"}), 400

    file = request.files["video"]
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name
        file.save(tmp_path)

    try:
        pose_feat = extract_pose_sequence(tmp_path)

        if pose_feat is None:
            return jsonify({"error": "Aucune pose détectée"}), 400

        tensor = torch.tensor(pose_feat).unsqueeze(0)
        with torch.no_grad():
            mean_feature = model(tensor, return_features=True).numpy()[0]

        db = load_encrypted_db()
        scores = {}
        for person_id, encrypted_vec in db.items():
            stored_vec = decrypt_feature(encrypted_vec)
            score = float(cosine_similarity(mean_feature, stored_vec))
            scores[person_id] = round(score, 4)

        result = identify_person(mean_feature)
        log_action("ANALYZE_VIDEO", f"Résultat: {result['person']} score={result['score']}")

        return jsonify({
            "result": result,
            "scores": scores,
            "silhouettes": [],
            "frames_analyzed": 30
        })
    finally:
        os.unlink(tmp_path)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "GaitPoseCNN", "persons": 5})

if __name__ == "__main__":
    log_action("STARTUP", "API démarrée")
    app.run(host=API_HOST, port=API_PORT, debug=False)