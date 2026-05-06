

from PIL import Image
import numpy as np
import io


def preprocess_image(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("L")
    image = image.resize((64, 64))

    image_array = np.array(image) / 255.0

    return image_array