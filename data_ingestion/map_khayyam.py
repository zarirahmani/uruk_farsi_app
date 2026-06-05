from pathlib import Path
import shutil
import csv

from data_ingestion.clean_images import clean_and_save_image


DATASET_DIR = Path("/Users/zahra/uruk/data/external/Khayyam_Dataset/2nd/Chars1")
OUTPUT_DIR = Path("data/interim/khayyam_letters_cleaned")
METADATA_PATH = Path("data/metadata/khayyam_letters_cleaned.csv")

# Maps folder number -> Persian character label.

FOLDER_LABEL_MAP = {
    1:  "آ",
    2:  "ا",
    3:  "ب",
    4:  "پ",
    5:  "ت",
    29: "م",
    30: "ن",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def main():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    total_saved = 0

    for folder_num, label in FOLDER_LABEL_MAP.items():
        source_dir = DATASET_DIR / str(folder_num)

        if not source_dir.exists():
            print(f"Warning: folder not found for label '{label}': {source_dir}")
            continue

        image_paths = [
            p for p in source_dir.rglob("*")
            if p.suffix.lower() in IMAGE_EXTENSIONS
        ]

        print(f"Folder {folder_num} ({label}): {len(image_paths)} images")

        for i, image_path in enumerate(image_paths):
            output_path = OUTPUT_DIR / label / f"khayyam_{label}_{i:06d}.png"

            success = clean_and_save_image(
                input_path=image_path,
                output_path=output_path,
                image_size=64,
            )

            if success:
                rows.append({
                    "source_dataset": "khayyam",
                    "original_path": str(image_path),
                    "cleaned_path": str(output_path),
                    "label": label,
                })
                total_saved += 1

    with open(METADATA_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["source_dataset", "original_path", "cleaned_path", "label"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {total_saved} cleaned images to {OUTPUT_DIR}")
    print(f"Metadata written to {METADATA_PATH}")


if __name__ == "__main__":
    main()
