from functions import load_image, split_image, process_image_parts, display_image_parts, save_image_parts

# Parameters
image_path = 'path_to_your_image.jpg'
n = 2  # Number of parts

# Load the image
image = load_image(image_path)

# Split the image into n parts
image_parts = split_image(image, n)

# Display the original parts
display_image_parts(image_parts, title_prefix="Original Part")

# Process the image parts in parallel
blurred_parts = process_image_parts(image_parts)

# Display the blurred parts
display_image_parts(blurred_parts, title_prefix="Blurred Part")

# Save the blurred parts if needed
save_image_parts(blurred_parts, prefix="blurred_part")
