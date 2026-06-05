from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image


DATA_DIR = Path("data/interim/khayyam_letters_cleaned")


def main():
    labels = ["آ", "ا", "ب", "پ", "ت", "م", "ن"]

    for label in labels:
        image_paths = list((DATA_DIR / label).glob("*.png"))[:5]

        if not image_paths:
            print(f"No images for {label}")
            continue

        for image_path in image_paths:
            image = Image.open(image_path)
            plt.imshow(image, cmap="gray")
            plt.title(f"{label}: {image_path.name}")
            plt.axis("off")
            plt.show()


if __name__ == "__main__":
    main()