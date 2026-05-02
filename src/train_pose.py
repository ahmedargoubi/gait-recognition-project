import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RAW_VIDEOS_DIR, FEATURES_DIR, NUM_PERSONS, FRAMES_PER_VIDEO
from src.model_pose import GaitPoseCNN
from src.pose_extractor import extract_pose_sequence

class PoseDataset(Dataset):
    def __init__(self):
        self.samples = []
        self.labels  = []

        videos = sorted([
            f for f in os.listdir(RAW_VIDEOS_DIR) if f.endswith('.mp4')
        ])

        for i, video_file in enumerate(videos):
            print(f"Extraction pose {video_file}...")
            path = os.path.join(RAW_VIDEOS_DIR, video_file)
            feat = extract_pose_sequence(path)
            if feat is not None:
                self.samples.append(feat)
                self.labels.append(i)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return (
            torch.tensor(self.samples[idx], dtype=torch.float32),
            torch.tensor(self.labels[idx],  dtype=torch.long)
        )


def train_pose_model():
    dataset = PoseDataset()
    loader  = DataLoader(dataset, batch_size=4, shuffle=True)

    model     = GaitPoseCNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print("\nEntraînement GaitPoseCNN...")
    for epoch in range(50):
        total_loss, correct, total = 0, 0, 0
        for feats, labels in loader:
            optimizer.zero_grad()
            out  = model(feats)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            correct    += out.argmax(1).eq(labels).sum().item()
            total      += labels.size(0)
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/50 | Loss: {total_loss:.4f} | Accuracy: {100*correct/total:.1f}%")

    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/gait_pose_model.pth")
    print("Modèle sauvegardé dans models/gait_pose_model.pth")

    # Sauvegarde des features par personne
    model.eval()
    videos = sorted([f for f in os.listdir(RAW_VIDEOS_DIR) if f.endswith('.mp4')])
    with torch.no_grad():
        for i, video_file in enumerate(videos):
            person_id = f"person_{i+1:02d}"
            path = os.path.join(RAW_VIDEOS_DIR, video_file)
            feat = extract_pose_sequence(path)
            if feat is not None:
                tensor = torch.tensor(feat).unsqueeze(0)
                vec    = model(tensor, return_features=True).numpy()[0]
                np.save(os.path.join(FEATURES_DIR, f"{person_id}.npy"), vec)
                print(f"Features pose {person_id} sauvegardées")

    print("Terminé !")

if __name__ == "__main__":
    train_pose_model()