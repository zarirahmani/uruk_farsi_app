import io
import json
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

from training.model_cnn import SimpleCNN
from data_ingestion.clean_images import preprocess_image


REGISTRY_PATH = Path("models/model_registry.json")


def load_model_metadata():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as file:
        registry = json.load(file)

    return registry["active_model"]


class HandwritingModel:
    def __init__(self):
        metadata = load_model_metadata()

        self.model_name = metadata["model_name"]
        self.model_version = metadata["model_version"]
        self.model_path = metadata["model_path"]
        self.labels = metadata["labels"]
        self.image_size = metadata.get("image_size", 64)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = SimpleCNN(num_classes=len(self.labels)).to(self.device)

        checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.5,), std=(0.5,)),
        ])

    def predict_from_bytes(self, image_bytes: bytes):
        image = Image.open(io.BytesIO(image_bytes)).convert("L")
        image = preprocess_image(image, self.image_size)
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted_index = torch.max(probabilities, dim=1)

        predicted_label = self.labels[predicted_index.item()]

        return predicted_label, float(confidence.item())