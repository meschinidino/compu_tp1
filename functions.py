from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
import multiprocessing


def load_image(image_path):
    # Load the image
    return Image.open(image_path)


def split_image(image, n):
    # Get image dimensions
    width, height = image.size

    # Calculate the width of each part
    part_width = width // n

    # Initialize a list to hold the image parts
    image_parts = []

    # Divide the image into n parts
    for i in range(n):
        left = i * part_width
        right = (i + 1) * part_width if i < n - 1 else width  # Ensure the last part takes the remaining width
        part = image.crop((left, 0, right, height))
        image_parts.append(part)

    return image_parts


def apply_filter(image_part):
    # Convert the PIL image to a NumPy array
    image_array = np.array(image_part)

    # Apply a Gaussian blur filter
    blurred_array = gaussian_filter(image_array, sigma=2)

    # Convert the NumPy array back to a PIL image
    blurred_image = Image.fromarray(blurred_array)

    return blurred_image


def process_image_parts(image_parts):
    with multiprocessing.Pool(processes=len(image_parts)) as pool:
        processed_parts = pool.map(apply_filter, image_parts)
    return processed_parts


def display_image_parts(image_parts, title_prefix="Part"):
    for i, part in enumerate(image_parts):
        part.show(title=f'{title_prefix} {i + 1}')


def save_image_parts(image_parts, prefix="part"):
    for i, part in enumerate(image_parts):
        part.save(f'{prefix}_{i + 1}.jpg')
