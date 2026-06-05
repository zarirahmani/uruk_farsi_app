from pathlib import Path
import shutil
from sklearn.model_selection import train_test_split


RAW_DIR = Path("data/interim/combined_data")
OUT_DIR = Path("data/processed_handwriting")

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"]


def reset_output_dir():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)

    for split in ["train", "val", "test"]:
        (OUT_DIR / split).mkdir(parents=True, exist_ok=True)


def get_image_files(label_dir: Path):
    return [
        path for path in label_dir.rglob("*")
        if path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def copy_files(files, destination_dir: Path):
    destination_dir.mkdir(parents=True, exist_ok=True)

    for file_path in files:
        shutil.copy2(file_path, destination_dir / file_path.name)


def split_label(label_dir: Path):
    label = label_dir.name
    image_files = get_image_files(label_dir)

    if len(image_files) < 10:
        print(f"Skipping {label}: only {len(image_files)} images")
        return

    train_files, temp_files = train_test_split(
        image_files,
        train_size=TRAIN_RATIO,
        random_state=42,
        shuffle=True,
    )

    val_size_adjusted = VAL_RATIO / (VAL_RATIO + TEST_RATIO)

    val_files, test_files = train_test_split(
        temp_files,
        train_size=val_size_adjusted,
        random_state=42,
        shuffle=True,
    )

    copy_files(train_files, OUT_DIR / "train" / label)
    copy_files(val_files, OUT_DIR / "val" / label)
    copy_files(test_files, OUT_DIR / "test" / label)

    print(
        f"{label}: "
        f"train={len(train_files)}, "
        f"val={len(val_files)}, "
        f"test={len(test_files)}"
    )


def main():
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Input folder not found: {RAW_DIR}")

    reset_output_dir()

    label_dirs = [
        path for path in RAW_DIR.iterdir()
        if path.is_dir()
    ]

    if not label_dirs:
        raise ValueError(f"No label folders found in {RAW_DIR}")

    for label_dir in sorted(label_dirs):
        split_label(label_dir)

    print(f"\nProcessed dataset saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()