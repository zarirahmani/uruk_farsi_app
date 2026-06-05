from pathlib import Path
import json
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import DataLoader
from torchvision import transforms

from training.dataset import FarsiHandwritingDataset
from training.model_cnn import SimpleCNN


LABELS = ["آ", "ا", "ب", "پ", "ت", "ن", "م"]

TRAIN_DIR = "data/processed_handwriting/train"
VAL_DIR = "data/processed_handwriting/val"

MODEL_DIR = Path("models")

MODEL_NAME = "handwriting_cnn"
MODEL_VERSION = "v0.1.0"
MODEL_PATH = MODEL_DIR / f"{MODEL_NAME}_{MODEL_VERSION}.pt"
REGISTRY_PATH = MODEL_DIR / "model_registry.json"

BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 0.001
RANDOM_SEED = 42


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()

    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for images, labels in dataloader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)

        predictions = outputs.argmax(dim=1)
        total_correct += (predictions == labels).sum().item()
        total_samples += labels.size(0)

    avg_loss = total_loss / total_samples
    accuracy = total_correct / total_samples

    return avg_loss, accuracy


def validate(model, dataloader, criterion, device):
    model.eval()

    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)

            predictions = outputs.argmax(dim=1)
            total_correct += (predictions == labels).sum().item()
            total_samples += labels.size(0)

    avg_loss = total_loss / total_samples
    accuracy = total_correct / total_samples

    return avg_loss, accuracy


def update_model_registry(best_val_accuracy: float):
    registry = {
        "active_model": {
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "model_path": str(MODEL_PATH),
            "labels": LABELS,
            "image_size": 64,
            "input_channels": 1,
            "best_val_accuracy": best_val_accuracy,
            "description": f"CNN trained on {len(LABELS)} Persian handwritten letters",
        }
    }

    with open(REGISTRY_PATH, "w", encoding="utf-8") as file:
        json.dump(registry, file, ensure_ascii=False, indent=2)


def main():
    MODEL_DIR.mkdir(exist_ok=True)
    set_seed(RANDOM_SEED)

    train_transform = transforms.Compose([
        transforms.RandomRotation(degrees=8),
        transforms.RandomAffine(
            degrees=0,
            translate=(0.08, 0.08),
            scale=(0.90, 1.10),
        ),
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.5,), std=(0.5,)),
    ])

    val_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.5,), std=(0.5,)),
    ])

    train_dataset = FarsiHandwritingDataset(
        root_dir=TRAIN_DIR,
        labels=LABELS,
        transform=train_transform,
    )

    val_dataset = FarsiHandwritingDataset(
        root_dir=VAL_DIR,
        labels=LABELS,
        transform=val_transform,
    )

    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = SimpleCNN(num_classes=len(LABELS)).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_val_accuracy = 0.0

    for epoch in range(EPOCHS):
        train_loss, train_accuracy = train_one_epoch(
            model=model,
            dataloader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
        )

        val_loss, val_accuracy = validate(
            model=model,
            dataloader=val_loader,
            criterion=criterion,
            device=device,
        )

        print(
            f"Epoch {epoch + 1:02d}/{EPOCHS} | "
            f"train_loss={train_loss:.4f} | "
            f"train_acc={train_accuracy:.4f} | "
            f"val_loss={val_loss:.4f} | "
            f"val_acc={val_accuracy:.4f}"
        )

        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "labels": LABELS,
                    "model_name": MODEL_NAME,
                    "model_version": MODEL_VERSION,
                    "image_size": 64,
                    "input_channels": 1,
                    "best_val_accuracy": best_val_accuracy,
                },
                MODEL_PATH,
            )

            update_model_registry(best_val_accuracy)

            print(f"Saved new best model to {MODEL_PATH}")

    print(f"Best validation accuracy: {best_val_accuracy:.4f}")


if __name__ == "__main__":
    main()