from pathlib import Path
import json
import pandas as pd
import torch
import matplotlib.pyplot as plt

from torch.utils.data import DataLoader
from torchvision import transforms
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

from training.dataset import FarsiHandwritingDataset
from training.model_cnn import SimpleCNN
from backend.app.database import init_db, log_metric


REGISTRY_PATH = Path("models/model_registry.json")
TEST_DIR = "data/processed_handwriting/test"
REPORT_DIR = Path("reports")

BATCH_SIZE = 32


def load_model_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as file:
        registry = json.load(file)

    return registry["active_model"]


def load_trained_model(model_info, device):
    labels = model_info["labels"]
    model_path = model_info["model_path"]

    model = SimpleCNN(num_classes=len(labels)).to(device)

    checkpoint = torch.load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    return model


def get_test_loader(labels):
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.5,), std=(0.5,)),
    ])

    test_dataset = FarsiHandwritingDataset(
        root_dir=TEST_DIR,
        labels=labels,
        transform=test_transform,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    return test_loader, test_dataset


def predict(model, dataloader, device):
    y_true = []
    y_pred = []

    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device)

            outputs = model(images)
            predictions = outputs.argmax(dim=1)

            y_true.extend(labels.tolist())
            y_pred.extend(predictions.cpu().tolist())

    return y_true, y_pred


def save_classification_report(y_true, y_pred, labels, model_info):
    report_dict = classification_report(
        y_true,
        y_pred,
        target_names=labels,
        output_dict=True,
        zero_division=0,
    )

    report_df = pd.DataFrame(report_dict).transpose()

    report_path = REPORT_DIR / (
        f"classification_report_{model_info['model_version']}.csv"
    )

    report_df.to_csv(report_path, encoding="utf-8")

    print("\nClassification report:")
    print(report_df)

    print(f"\nSaved classification report to: {report_path}")


def save_confusion_matrix(y_true, y_pred, labels, model_info):
    cm = confusion_matrix(y_true, y_pred)

    cm_df = pd.DataFrame(
        cm,
        index=[f"true_{label}" for label in labels],
        columns=[f"pred_{label}" for label in labels],
    )

    csv_path = REPORT_DIR / f"confusion_matrix_{model_info['model_version']}.csv"
    cm_df.to_csv(csv_path, encoding="utf-8")

    print("\nConfusion matrix:")
    print(cm_df)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(cm, cmap="Blues")

    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    for i in range(len(labels)):
        for j in range(len(labels)):
            color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, cm[i, j], ha="center", va="center", color=color)

    image_path = REPORT_DIR / f"confusion_matrix_{model_info['model_version']}.png"
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

    print(f"\nSaved confusion matrix CSV to: {csv_path}")
    print(f"Saved confusion matrix image to: {image_path}")


def save_predictions(y_true, y_pred, labels, model_info):
    rows = []

    for true_idx, pred_idx in zip(y_true, y_pred):
        rows.append({
            "true_label": labels[true_idx],
            "predicted_label": labels[pred_idx],
            "is_correct": true_idx == pred_idx,
        })

    predictions_df = pd.DataFrame(rows)

    predictions_path = REPORT_DIR / f"test_predictions_{model_info['model_version']}.csv"
    predictions_df.to_csv(predictions_path, index=False, encoding="utf-8")

    print(f"Saved test predictions to: {predictions_path}")


def log_evaluation_metrics_to_db(y_true, y_pred, labels, model_info):
    init_db()

    model_name = model_info["model_name"]
    model_version = model_info["model_version"]

    accuracy = accuracy_score(y_true, y_pred)

    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0,
    )
    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0,
    )

    overall_metrics = {
        "test_accuracy": accuracy,
        "test_macro_precision": macro_precision,
        "test_macro_recall": macro_recall,
        "test_macro_f1": macro_f1,
        "test_weighted_precision": weighted_precision,
        "test_weighted_recall": weighted_recall,
        "test_weighted_f1": weighted_f1,
    }

    for metric_name, metric_value in overall_metrics.items():
        log_metric(
            model_name=model_name,
            model_version=model_version,
            metric_name=metric_name,
            metric_value=float(metric_value),
        )

    per_class_precision, per_class_recall, per_class_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=list(range(len(labels))), zero_division=0,
    )

    for label, precision, recall, f1 in zip(
        labels, per_class_precision, per_class_recall, per_class_f1,
    ):
        log_metric(model_name=model_name, model_version=model_version,
                   metric_name=f"test_precision_{label}", metric_value=float(precision))
        log_metric(model_name=model_name, model_version=model_version,
                   metric_name=f"test_recall_{label}", metric_value=float(recall))
        log_metric(model_name=model_name, model_version=model_version,
                   metric_name=f"test_f1_{label}", metric_value=float(f1))

    print("Logged evaluation metrics to SQLite.")


def main():
    REPORT_DIR.mkdir(exist_ok=True)
    model_info = load_model_registry()

    labels = model_info["labels"]
    model_version = model_info["model_version"]

    print(f"Evaluating model version: {model_version}")
    print(f"Labels: {labels}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = load_trained_model(model_info, device)

    test_loader, test_dataset = get_test_loader(labels)

    print(f"Test samples: {len(test_dataset)}")

    y_true, y_pred = predict(model, test_loader, device)

    accuracy = accuracy_score(y_true, y_pred)

    print(f"\nTest accuracy: {accuracy:.4f}")

    save_classification_report(y_true, y_pred, labels, model_info)
    save_confusion_matrix(y_true, y_pred, labels, model_info)
    save_predictions(y_true, y_pred, labels, model_info)
    log_evaluation_metrics_to_db(y_true, y_pred, labels, model_info)
    model_info["test_accuracy"] = float(accuracy)

    with open(REGISTRY_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {"active_model": model_info},
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Updated model registry: {REGISTRY_PATH}")


if __name__ == "__main__":
    main()