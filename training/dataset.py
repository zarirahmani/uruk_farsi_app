# This module is for feeding already-prepared images into PyTorch.


from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset


class FarsiHandwritingDataset(Dataset):
    def __init__(self, root_dir, labels, transform=None):
        self.root_dir = Path(root_dir)
        self.labels = labels
        self.label_to_index = {label: idx for idx, label in enumerate(labels)}
        self.transform = transform
        self.samples = []

        for label in labels:
            label_dir = self.root_dir / label

            if not label_dir.exists():
                print(f"Warning: missing label folder: {label_dir}")
                continue

            for image_path in label_dir.glob("*.png"):
                self.samples.append((image_path, self.label_to_index[label]))

        if not self.samples:
            raise ValueError(f"No images found in {self.root_dir}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        image_path, label_index = self.samples[index]

        image = Image.open(image_path).convert("L")

        if self.transform:
            image = self.transform(image)

        return image, label_index