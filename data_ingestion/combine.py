from pathlib import Path
import shutil

from data_ingestion.clean_images import clean_and_save_image


TARGET_LABELS = ["آ", "ا", "ب", "پ", "ت", "م", "ن"]

KHAYYAM_DIR = Path("data/interim/khayyam_letters_cleaned")
APP_RAW_DIR = Path("data/raw_handwriting")
OUTPUT_DIR = Path("data/interim/combined_data")


def copy_khayyam_cleaned():
    count = 0

    for label in TARGET_LABELS:
        source_dir = KHAYYAM_DIR / label
        target_dir = OUTPUT_DIR / label
        target_dir.mkdir(parents=True, exist_ok=True)

        if not source_dir.exists():
            print(f"Warning: Khayyam folder not found for '{label}': {source_dir}")
            continue

        for image_path in source_dir.glob("*.png"):
            shutil.copy2(image_path, target_dir / image_path.name)
            count += 1

    print(f"Copied Khayyam images: {count}")
    return count


def clean_app_data():
    count = 0

    for label in TARGET_LABELS:
        source_dir = APP_RAW_DIR / label

        if not source_dir.exists():
            print(f"Warning: app folder not found for '{label}': {source_dir}")
            continue

        for i, image_path in enumerate(source_dir.glob("*.png")):
            output_path = OUTPUT_DIR / label / f"app_{label}_{i:06d}.png"

            success = clean_and_save_image(image_path, output_path)

            if success:
                count += 1

    print(f"Cleaned app images: {count}")
    return count


def main():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    khayyam_count = copy_khayyam_cleaned()
    app_count = clean_app_data()

    print(f"Total combined: {khayyam_count + app_count} images saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()