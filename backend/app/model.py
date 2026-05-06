import json
from pathlib import Path
import random


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

    def predict(self, image_array):
        """
        Placeholder model.
        Replace this later with a CNN prediction.
        """
        possible_labels = ["ا", "ب", "پ", "ت", "ن", "م"]
        predicted_label = random.choice(possible_labels)
        confidence = round(random.uniform(0.60, 0.98), 2)

        return predicted_label, confidence