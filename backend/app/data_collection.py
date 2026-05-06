from pathlib import Path
from datetime import datetime
import csv


RAW_DATA_DIR = Path("data/raw_handwriting")
METADATA_DIR = Path("data/metadata")
METADATA_FILE = METADATA_DIR / "handwriting_attempts.csv"


def ensure_data_dirs():
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


def save_handwriting_image(
    image_bytes: bytes,
    target_label: str,
    learner_id: str,
    exercise_id: str,
) -> str:
    """
    Saves the raw learner drawing into a folder named by target label.
    """

    ensure_data_dirs()

    label_dir = RAW_DATA_DIR / target_label
    label_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")

    filename = f"{learner_id}_{exercise_id}_{timestamp}.png"
    image_path = label_dir / filename

    with open(image_path, "wb") as file:
        file.write(image_bytes)

    return str(image_path)


def append_metadata(row: dict):
    """
    Appends one attempt record to handwriting_attempts.csv.
    """

    ensure_data_dirs()

    file_exists = METADATA_FILE.exists()

    fieldnames = [
        "image_path",
        "target_label",
        "predicted_label",
        "learner_id",
        "exercise_id",
        "confidence",
        "is_correct",
        "model_name",
        "model_version",
        "timestamp",
    ]

    with open(METADATA_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)