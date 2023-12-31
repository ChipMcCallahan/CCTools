import os
from PIL import Image

def get_image_sizes(directory):
    """Prints the size of all BMP and PNG files in the given directory."""
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.bmp', '.png')):
            filepath = os.path.join(directory, filename)
            with Image.open(filepath) as img:
                print(f"{filename}: {img.size} pixels")

if __name__ == "__main__":
    # Use the current directory
    directory_path = os.getcwd()
    get_image_sizes(directory_path)

