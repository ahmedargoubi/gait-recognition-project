import torch
import torch.nn as nn
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FEATURE_DIM, NUM_PERSONS

class GaitCNN(nn.Module):
    def __init__(self):
        super(GaitCNN, self).__init__()
        
        # 3 couches convolutionnelles
        self.conv_layers = nn.Sequential(
            # Couche 1
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            # Couche 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            # Couche 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        
        # Couche fully connected → vecteur 128D
        self.feature_layer = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 8 * 8, FEATURE_DIM),
            nn.ReLU(),
        )
        
        # Couche de classification finale
        self.classifier = nn.Linear(FEATURE_DIM, NUM_PERSONS)

    def forward(self, x, return_features=False):
        x = self.conv_layers(x)
        features = self.feature_layer(x)
        if return_features:
            return features  # vecteur 128D pour identification
        return self.classifier(features)

if __name__ == "__main__":
    model = GaitCNN()
    print(model)
    dummy = torch.zeros(1, 1, 64, 64)
    out = model(dummy, return_features=True)
    print(f"Vecteur features : {out.shape}")  # doit afficher torch.Size([1, 128])