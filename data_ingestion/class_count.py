from pathlib import Path


DATA_DIR = Path("data/processed_handwriting")


def count_images(split):
    split_dir = DATA_DIR / split

    print(f"\n{split.upper()}")

    for label_dir in sorted(split_dir.iterdir()):
        if label_dir.is_dir():
            count = len(list(label_dir.glob("*.png")))
            print(f"{label_dir.name}: {count}")


def main():
    for split in ["train", "val", "test"]:
        count_images(split)


if __name__ == "__main__":
    main()