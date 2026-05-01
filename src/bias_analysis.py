import numpy as np
import os
import sys
import torch
import cv2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SILHOUETTES_DIR, FEATURES_DIR, IMG_SIZE, NUM_PERSONS
from src.model import GaitCNN
from src.identify import identify_person

def compute_metrics():
    """Calcule accuracy, FAR et FRR sur le dataset"""
    model = GaitCNN()
    model.load_state_dict(torch.load("models/gait_model.pth", weights_only=True))
    model.eval()

    correct = 0
    total = 0
    false_accept = 0
    false_reject = 0

    with torch.no_grad():
        for person_id in range(1, NUM_PERSONS + 1):
            person_dir = os.path.join(SILHOUETTES_DIR, f"person_{person_id:02d}")
            for img_file in os.listdir(person_dir):
                img_path = os.path.join(person_dir, img_file)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                img = cv2.resize(img, IMG_SIZE).astype(np.float32) / 255.0
                tensor = torch.tensor(img).unsqueeze(0).unsqueeze(0)
                feat = model(tensor, return_features=True).numpy()[0]
                result = identify_person(feat)
                expected = f"person_{person_id:02d}"
                total += 1
                if result["status"] == "identified" and result["person"] == expected:
                    correct += 1
                elif result["status"] == "identified" and result["person"] != expected:
                    false_accept += 1
                elif result["status"] == "unknown":
                    false_reject += 1

    accuracy = 100.0 * correct / total
    far = 100.0 * false_accept / total
    frr = 100.0 * false_reject / total

    print("=" * 40)
    print("RAPPORT D'ÉVALUATION DU MODÈLE")
    print("=" * 40)
    print(f"Total échantillons  : {total}")
    print(f"Accuracy            : {accuracy:.1f}%")
    print(f"FAR (Faux Acceptés) : {far:.1f}%")
    print(f"FRR (Faux Rejetés)  : {frr:.1f}%")
    print("=" * 40)
    print("ANALYSE DES BIAIS")
    print("=" * 40)
    print("- Dataset limité (5 personnes) : risque de surapprentissage")
    print("- Vidéos Pexels : biais possible sur l'angle de vue")
    print("- Pas de diversité morphologique garantie")
    print("- Recommandation : augmenter à 20+ personnes en production")
    return accuracy, far, frr

if __name__ == "__main__":
    compute_metrics()