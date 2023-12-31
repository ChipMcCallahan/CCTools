"""Assorted PIL Image tranformation utils."""

import importlib.resources
from PIL import Image, ImageOps, ImageDraw, ImageFont

RED = "RED"
YELLOW = "YELLOW"
GREEN = "GREEN"
BLUE = "BLUE"
BROWN = "BROWN"

COLORS = {
    RED: "#FF0000",
    YELLOW: "#FFFF00",
    GREEN: "#00FF00",
    BLUE: "#0000FF",
    BROWN: "#A52A2A"
}


def add_text_label_to_image(image, text, position=(0, 0), font_size=10,
                            padding=2):
    """
    Draws right-justified text on a PIL image with a black box behind the text.

    Args: image (PIL.Image.Image): The image on which to draw the text. text
    (str): The text to be drawn. position (tuple): The position (x, y) where
    the right edge of the text will be aligned. font_size (int): The font
    size of the text. padding (int): Padding around the text inside the box.

    Returns: PIL.Image.Image: The image with the right-justified text and
    black box drawn on it.
    """
    draw = ImageDraw.Draw(image)

    # Optionally use a truetype font
    # font = ImageFont.truetype("arial.ttf", font_size)
    # For simplicity, using default font
    font = ImageFont.load_default()

    # Calculate text width using textlength and height using font size
    text_width = draw.textlength(text, font=font)
    # Approximation, as the actual height depends on the font
    text_height = font_size

    # Calculate box dimensions
    box_width = text_width + 2 * padding
    box_height = text_height + 2 * padding

    # Adjust position to right-justify the text
    text_position = (position[0] - text_width, position[1])

    # Calculate box position
    box_position = (text_position[0] - padding, text_position[1] - padding,
                    text_position[0] + box_width - padding,
                    text_position[1] + box_height - padding)

    # Draw the black box
    draw.rectangle(box_position, fill="black")

    # Draw the text
    draw.text(text_position, text, fill="white",
              font=font)  # White color for text for contrast

    return image


def colorize(img, color):
    """
    Colorize an image while maintaining its transparency.

    Args:
        img (PIL.Image.Image): The image to be colorized.
        color (str): The color to apply to the image.

    Returns:
        PIL.Image.Image: The colorized image.
    """
    _, _, _, alpha = img.split()
    img_gray = ImageOps.grayscale(img)
    img_new = ImageOps.colorize(img_gray, "#00000000", COLORS.get(color))
    img_new.putalpha(alpha)
    return img_new


def draw_red_line(image, x1, y1, x2, y2):
    """
    Draws a red line on a PIL image.

    Args:
    image (PIL.Image.Image): The image on which to draw the line.
    x1, y1 (int, int): The starting coordinates of the line.
    x2, y2 (int, int): The ending coordinates of the line.

    Returns:
    PIL.Image.Image: The image with the red line drawn on it.
    """
    draw = ImageDraw.Draw(image)
    draw.line((x1, y1, x2, y2), fill="red", width=1)

    return image


def load_sprite_file(package, filename):
    """
    Load a sprite image from a file within the specified package.

    Args:
        package (str): The package path of the sprite image to load.
        filename (str): The filename of the sprite image to load.

    Returns:
        PIL.Image.Image: The loaded sprite image.
    """
    with importlib.resources.path(package, filename) as path:
        image = Image.open(path)
        return image.convert('RGBA')


def make_transparent(image, colors):
    """
    Makes specified colors in a PIL Image object transparent.

    Args: image (PIL.Image.Image): The image to process. colors (list or
    tuple): A list or tuple of color values to make transparent. Each
    color should be in the format (R, G, B) or (R, G, B, A).

    Returns:
    PIL.Image.Image: A new image with specified colors made transparent.
    """

    # Ensure image is in RGBA mode
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Create a new image for output
    new_image = Image.new('RGBA', image.size)
    width, height = image.size

    # Iterate through each pixel
    for x in range(width):
        for y in range(height):
            current_color = image.getpixel((x, y))

            # Check if the current color matches any in the list
            if current_color[:3] in [color[:3] for color in colors]:
                # Make transparent
                new_image.putpixel((x, y), (0, 0, 0, 0))
            else:
                # Copy pixel
                new_image.putpixel((x, y), current_color)

    return new_image


def create_transparent_image(white_tile, black_tile):
    """
    Creates a transparent image from two tiles: one on a white
    background and one on a black background. Any pixel that is white in
    the white image and black in the black image becomes transparent.

    Args:
        white_tile (PIL.Image.Image): The tile image on a white background.
        black_tile (PIL.Image.Image): The tile image on a black background.

    Returns: PIL.Image.Image: A new image with specified pixels made
    transparent.
    """

    # Ensure both images are in RGBA mode
    white_tile = white_tile.convert("RGBA")
    black_tile = black_tile.convert("RGBA")

    width, height = white_tile.size
    transparent_img = Image.new("RGBA", (width, height))

    for y in range(height):
        for x in range(width):
            white_pixel = white_tile.getpixel((x, y))
            black_pixel = black_tile.getpixel((x, y))

            # Check if the pixel is white in white_tile and black in
            # black_tile
            if white_pixel[:3] == (255, 255, 255) and black_pixel[:3] == (
                    0, 0, 0):
                # Make the pixel fully transparent
                alpha = 0
            else:
                # Keep the pixel from the white_tile and fully opaque
                alpha = 255

            new_pixel = (*white_pixel[:3], alpha)
            transparent_img.putpixel((x, y), new_pixel)

    return transparent_img


def apply_transparent_circle_to_image(base_image):
    """
    Applies a transparent circle to an existing image. The transparency
    decreases as one moves away from the center.

    Args: base_image (PIL.Image.Image): The existing image to which the
    transparent circle will be applied.

    Returns:
    PIL.Image.Image: The image with the applied transparent circle.
    """
    # Ensure base image is in RGBA mode
    base_image = base_image.convert("RGBA")
    image_size = base_image.size[0]  # Assuming the image is square

    # Create a new image for the alpha mask
    alpha_mask = Image.new("L", (image_size, image_size), 0)

    # Center and radius for the circle
    center = (image_size // 2, image_size // 2)
    radius = image_size // 2

    for y in range(image_size):
        for x in range(image_size):
            # Distance from the center
            distance = ((x - center[0]) ** 2 + (y - center[1]) ** 2) ** 0.5

            # Calculate the alpha value based on the distance. The alpha
            # value increases as the distance from the center increases
            alpha = int(255 * min(distance / radius, 1))

            # Set the pixel in the alpha mask
            alpha_mask.putpixel((x, y), alpha)

    # Combine the base image with the alpha mask
    base_image.putalpha(alpha_mask)

    return base_image
