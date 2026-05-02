import torch
import torch.nn as nn
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import NUM_PERSONS

POSE_INPUT_DIM = 30 * 20  # 600 valeurs (30 frames × 20 features)
FEATURE_DIM = 128

class GaitPoseCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv_layers = nn.Sequential(
            nn.Conv1d(1, 64, kernel_size=7, padding=3),
            nn.ReLU(),
            nn.MaxPool1d(2),          # 600 → 300

            nn.Conv1d(64, 128, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(2),          # 300 → 150

            nn.Conv1d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),          # 150 → 75
        )

        # 256 × 75 = 19200
        self.feature_layer = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 75, FEATURE_DIM),
            nn.ReLU(),
            nn.Dropout(0.3),
        )

        self.classifier = nn.Linear(FEATURE_DIM, NUM_PERSONS)

    def forward(self, x, return_features=False):
        x = x.unsqueeze(1)           # (batch, 600) → (batch, 1, 600)
        x = self.conv_layers(x)      # → (batch, 256, 75)
        features = self.feature_layer(x)
        if return_features:
            return features
        return self.classifier(features)

if __name__ == "__main__":
    model = GaitPoseCNN()
    dummy = torch.zeros(1, POSE_INPUT_DIM)
    out = model(dummy, return_features=True)
    print(f"Modèle GaitPoseCNN OK — feature shape: {out.shape}")
    # doit afficher : torch.Size([1, 128])