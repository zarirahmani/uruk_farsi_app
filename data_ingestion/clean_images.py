from pathlib import Path
from PIL import Image, ImageOps
import numpy as np


def is_blank_image(image: Image.Image, threshold: float = 0.995) -> bool:
    gray = image.convert("L")
    arr = np.array(gray)

    dark_pixels = arr < 240
    dark_ratio = dark_pixels.mean()

    return dark_ratio < (1 - threshold)


def crop_to_ink(image: Image.Image, padding: int = 8) -> Image.Image:
    gray = image.convert("L")
    arr = np.array(gray)

    ink_mask = arr < 240

    if not ink_mask.any():
        return image

    ys, xs = np.where(ink_mask)

    left = max(xs.min() - padding, 0)
    right = min(xs.max() + padding, image.width)
    top = max(ys.min() - padding, 0)
    bottom = min(ys.max() + padding, image.height)

    return image.crop((left, top, right, bottom))


def preprocess_image(image: Image.Image, image_size: int = 64) -> Image.Image:
    image = crop_to_ink(image)

    return ImageOps.pad(
        image,
        size=(image_size, image_size),
        color=255,
        centering=(0.5, 0.5),
    )


def clean_and_save_image(
    input_path: Path,
    output_path: Path,
    image_size: int = 64,
) -> bool:
    image = Image.open(input_path).convert("L")

    if is_blank_image(image):
        return False

    image = preprocess_image(image, image_size)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

    return True