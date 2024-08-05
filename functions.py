from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
import multiprocessing
import signal
import sys

def load_image(image_path):
    return Image.open(image_path)

def split_image(image, n):
    width, height = image.size
    part_width = width // n
    image_parts = []

    for i in range(n):
        left = i * part_width
        right = (i + 1) * part_width if i < n - 1 else width
        part = image.crop((left, 0, right, height))
        image_parts.append(part)

    return image_parts

def apply_filter(image_part, pipe_conn):
    image_array = np.array(image_part)
    blurred_array = gaussian_filter(image_array, sigma=2)
    blurred_image = Image.fromarray(blurred_array)
    pipe_conn.send(np.array(blurred_image))
    pipe_conn.close()

def process_image_parts_with_pipes(image_parts):
    parent_conns, child_conns = zip(*[multiprocessing.Pipe() for _ in image_parts])
    processes = []

    for part, child_conn in zip(image_parts, child_conns):
        p = multiprocessing.Process(target=apply_filter, args=(part, child_conn))
        processes.append(p)
        p.start()

    processed_parts = [Image.fromarray(parent_conn.recv()) for parent_conn in parent_conns]
    for p in processes:
        p.join()

    return processed_parts

def signal_handler(sig, frame):
    print('Signal received, cleaning up...')
    sys.exit(0)

def setup_signal_handling():
    signal.signal(signal.SIGINT, signal_handler)

def store_part_in_shared_memory(shared_array, part_index, image_part, width, height):
    image_array = np.array(image_part)
    flattened = image_array.flatten()
    start = part_index * width * height * 3
    end = start + len(flattened)
    shared_array[start:end] = flattened

def create_shared_memory(image_parts):
    width, height = image_parts[0].size
    total_size = width * height * len(image_parts) * 3
    return multiprocessing.Array('B', total_size), width, height

def load_shared_memory_part(shared_array, part_index, width, height):
    start = part_index * width * height * 3
    end = start + width * height * 3
    image_array = np.frombuffer(shared_array.get_obj(), dtype=np.uint8)[start:end]
    return Image.fromarray(image_array.reshape((height, width, 3)))

def use_shared_memory(image_parts):
    shared_array, width, height = create_shared_memory(image_parts)

    processes = []
    for i, part in enumerate(image_parts):
        p = multiprocessing.Process(target=store_part_in_shared_memory, args=(shared_array, i, part, width, height))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    final_parts = [load_shared_memory_part(shared_array, i, width, height) for i in range(len(image_parts))]
    return final_parts

def save_image_parts(image_parts, prefix="part"):
    for i, part in enumerate(image_parts):
        part.save(f"{prefix}_{i + 1}.png")
        print(f"{prefix} {i + 1} saved as {prefix}_{i + 1}.png")

def save_combined_image(final_parts, output_filename="combined_image.png"):
    total_width = sum(part.size[0] for part in final_parts)
    height = final_parts[0].size[1]

    combined_image = Image.new("RGB", (total_width, height))

    x_offset = 0
    for part in final_parts:
        combined_image.paste(part, (x_offset, 0))
        x_offset += part.size[0]

    combined_image.save(output_filename)
    print(f"Combined image saved as {output_filename}")

def process_image(image_path, n):
    setup_signal_handling()
    image = load_image(image_path)
    image_parts = split_image(image, n)
    blurred_parts = process_image_parts_with_pipes(image_parts)
    save_image_parts(blurred_parts, prefix="blurred_part")
    final_parts = use_shared_memory(blurred_parts)
    save_combined_image(final_parts, output_filename="final_combined_image.png")
