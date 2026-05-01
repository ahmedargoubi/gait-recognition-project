import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
import cv2
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SILHOUETTES_DIR, FEATURES_DIR, IMG_SIZE, NUM_PERSONS, FEATURE_DIM
from src.model import GaitCNN

class GaitDataset(Dataset):
    def __init__(self):
        self.samples = []
        self.labels = []
        for person_id in range(1, NUM_PERSONS + 1):
            person_dir = os.path.join(SILHOUETTES_DIR, f"person_{person_id:02d}")
            for img_file in os.listdir(person_dir):
                img_path = os.path.join(person_dir, img_file)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                img = cv2.resize(img, IMG_SIZE)
                img = img.astype(np.float32) / 255.0
                self.samples.append(img)
                self.labels.append(person_id - 1)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img = torch.tensor(self.samples[idx]).unsqueeze(0)
        label = torch.tensor(self.labels[idx], dtype=torch.long)
        return img, label

def train_model():
    dataset = GaitDataset()
    loader = DataLoader(dataset, batch_size=16, shuffle=True)

    model = GaitCNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print("Entraînement en cours...")
    for epoch in range(30):
        total_loss = 0
        correct = 0
        total = 0
        for imgs, labels in loader:
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
        acc = 100. * correct / total
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/30 | Loss: {total_loss:.4f} | Accuracy: {acc:.1f}%")

    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/gait_model.pth")
    print("Modèle sauvegardé dans models/gait_model.pth")

    # Sauvegarde des features par personne
    model.eval()
    print("Extraction des features...")
    with torch.no_grad():
        for person_id in range(1, NUM_PERSONS + 1):
            person_dir = os.path.join(SILHOUETTES_DIR, f"person_{person_id:02d}")
            features_list = []
            for img_file in os.listdir(person_dir):
                img_path = os.path.join(person_dir, img_file)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                img = cv2.resize(img, IMG_SIZE).astype(np.float32) / 255.0
                tensor = torch.tensor(img).unsqueeze(0).unsqueeze(0)
                feat = model(tensor, return_features=True).numpy()
                features_list.append(feat[0])
            mean_feature = np.mean(features_list, axis=0)
            save_path = os.path.join(FEATURES_DIR, f"person_{person_id:02d}.npy")
            np.save(save_path, mean_feature)
            print(f"Features person_{person_id:02d} sauvegardées")

    print("Entraînement terminé !")
    return model

if __name__ == "__main__":
    train_model()