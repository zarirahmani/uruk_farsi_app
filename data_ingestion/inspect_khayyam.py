from pathlib import Path
from PIL import Image


DATASET_DIR = Path("/Users/zahra/uruk/data/external/Khayyam_Dataset/2nd/Chars1")

FOLDERS_TO_INSPECT = [1, 2, 3, 4, 5, 29, 30]

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def inspect_folder(folder_path: Path) -> None:
    images = [p for p in folder_path.rglob("*") if p.suffix.lower() in IMAGE_EXTENSIONS]
    print(f"\nFolder {folder_path.name}: {len(images)} images")

    for image_path in images[:3]:
        image = Image.open(image_path)
        print(f"  {image_path.name}  size={image.size}  mode={image.mode}")


def main():
    for folder_num in FOLDERS_TO_INSPECT:
        folder_path = DATASET_DIR / str(folder_num)
        if not folder_path.exists():
            print(f"Warning: folder not found: {folder_path}")
            continue
        inspect_folder(folder_path)


if __name__ == "__main__":
    main()
