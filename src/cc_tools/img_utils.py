"""Assorted PIL Image tranformation utils."""

import importlib.resources
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance

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


def create_bounding_box_transparency(tile, bounding_box):
    """
    Create a version of an image with everything outside a given bounding
    box made transparent.

    Args: tile (PIL.Image): The image to be processed. bounding_box (tuple):
    A tuple of (x1, y1, x2, y2) representing the bounding box.

    Returns:
    PIL.Image: A new image with transparency applied outside the bounding box.
    """
    if tile.mode != 'RGBA':
        raise ValueError("Tile must be in RGBA mode")

    # Create a transparent base image of the same size as 'tile'
    transparent_base = Image.new('RGBA', tile.size, (0, 0, 0, 0))

    # Crop the tile according to the bounding box
    cropped_tile = tile.crop(bounding_box)

    # Calculate the position to paste the cropped tile onto the transparent
    # base
    paste_x, paste_y = bounding_box[0], bounding_box[1]

    # Paste the cropped tile onto the transparent base
    transparent_base.paste(cropped_tile, (paste_x, paste_y), cropped_tile)

    return transparent_base


def compass_paste_16(image, direction):
    """
    Paste a 16x16 PIL image on a 32x32 transparent image, centered on the
    specified side.

    Args: image (PIL.Image): A 16x16 PIL image. direction (str): One of "N",
    "E", "S", "W" indicating the side to paste the image.

    Returns: PIL.Image: A 32x32 transparent image with the 16x16 image
    pasted as specified.
    """
    if image.size != (16, 16):
        raise ValueError("Image must be 16x16 pixels in size")

    # Create a 32x32 transparent image
    output_image = Image.new('RGBA', (32, 32), (0, 0, 0, 0))

    # Define paste positions based on direction
    paste_positions = {
        "N": (8, 0),  # Centered on the north side
        "E": (16, 8),  # Centered on the east side
        "S": (8, 16),  # Centered on the south side
        "W": (0, 8)  # Centered on the west side
    }

    if direction not in paste_positions:
        raise ValueError("Direction must be one of 'N', 'E', 'S', 'W'")

    # Paste the 16x16 image onto the 32x32 image at the specified position
    paste_position = paste_positions[direction]
    output_image.paste(image, paste_position)

    return output_image


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


def flatten(*images):
    """
    Flatten multiple PIL.Image objects into a single image.

    Args: *images: A variable number of PIL.Image objects in RGBA mode and
    of the same size.

    Returns:
    A single PIL.Image object in RGBA mode with all images pasted together,
    with the first image at the bottom and the last on top.
    """
    if not images:
        raise ValueError("No images provided")

    # Check if all images are in 'RGBA' mode and have the same size
    base_image = images[0]
    if base_image.mode != 'RGBA':
        raise ValueError("All images must be in RGBA mode")

    for img in images:
        if img.mode != 'RGBA' or img.size != base_image.size:
            raise ValueError(
                "All images must be in RGBA mode and have the same size")

    # Create a new image to paste all others onto
    output_image = Image.new('RGBA', base_image.size)

    # Paste each image onto the output image
    for img in images:
        output_image.paste(img, (0, 0), img)

    return output_image


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


def apply_alpha_mask(base_image, alpha_mask):
    """
    Replace the alpha channel of the base image with the alpha mask.

    Args:
        base_image (PIL.Image.Image): The base image in RGBA format.
        alpha_mask (PIL.Image.Image): The alpha mask.

    Returns:
        PIL.Image.Image: The resulting image with the alpha channel replaced.
    """

    # Convert the base image to 'RGBA' if it's not already
    base_image = base_image.convert("RGBA")

    # Convert the alpha mask to 'L' (grayscale) mode
    alpha_mask = alpha_mask.convert("L")

    # Split the base image into its R, G, B, and A channels
    r, g, b, _ = base_image.split()

    # Merge the R, G, B channels with the new alpha mask
    result_img = Image.merge("RGBA", (r, g, b, alpha_mask))

    return result_img


def make_semi_transparent(base_image):
    """
        Applies a transparent square to an existing image. The transparency
        increases exponentially as one moves closer to the center.

        Args:
            base_image (PIL.Image.Image): The existing image to which the
            transparent square will be applied.

        Returns:
            PIL.Image.Image: The image with the applied transparent square.
        """
    # Ensure base image is in RGBA mode
    base_image = base_image.convert("RGBA")
    image_size = base_image.size[0]  # Assuming the image is square

    # Create a new image for the alpha mask
    alpha_mask = Image.new("L", (image_size, image_size), 0)

    # Center for the square
    center = (image_size / 2 - 0.5, image_size / 2 - 0.5)
    max_distance = min(center)  # Maximum distance from center to corner

    for y in range(image_size):
        for x in range(image_size):
            distance = max(abs(x - center[0]), abs(y - center[1]))

            # Calculate the alpha value based on the distance, making it
            # exponentially transparent as it gets closer to the center
            alpha = int(255 * (
                    distance / max_distance) ** 2)  # Exponential decrease

            # Set the pixel in the alpha mask
            alpha_mask.putpixel((x, y), alpha)

    # Combine the base image with the alpha mask
    base_image.putalpha(alpha_mask)

    return base_image


def lighten_image(image, percentage):
    """
    Lighten an image by a certain percentage.

    Args:
        image (PIL.Image.Image): The image to lighten.
        percentage (float): The percentage to lighten the image.
                            0% means no change, 100% means pure white.

    Returns:
        PIL.Image.Image: The lightened image.
    """

    # Ensure percentage is in a valid range
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")

    # Calculate enhancement factor (1.0 means no change, 2.0 means double
    # brightness)
    factor = 1 + (percentage / 100)

    # Create a brightness enhancer
    enhancer = ImageEnhance.Brightness(image)

    # Enhance the image
    lightened_image = enhancer.enhance(factor)

    return lightened_image


def draw_directional_arrow(size, direction, arrow_color='red'):
    """
    Draw a directional arrow on an NxN tile with a transparent background.
    The arrow takes up a quarter of the tile and is positioned on the edge.

    Args:
        size (int): The size of the NxN tile (in pixels).
        direction (str): The direction of the arrow ('N', 'S', 'W', 'E').
        arrow_color (str): The color of the arrow (default is 'red').

    Returns:
        PIL.Image.Image: The image with the drawn arrow.
    """
    # Create a blank image with a transparent background
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Define the smaller arrow size and offset from center
    arrow_size = size // 4
    offset = size // 8

    # Define points for the arrow based on the direction
    if direction == 'N':
        points = [(size // 2, offset),
                  (size // 2 - arrow_size, offset + arrow_size),
                  (size // 2 + arrow_size, offset + arrow_size)]
    elif direction == 'S':
        points = [(size // 2, size - offset),
                  (size // 2 - arrow_size, size - offset - arrow_size),
                  (size // 2 + arrow_size, size - offset - arrow_size)]
    elif direction == 'W':
        points = [(offset, size // 2),
                  (offset + arrow_size, size // 2 - arrow_size),
                  (offset + arrow_size, size // 2 + arrow_size)]
    elif direction == 'E':
        points = [(size - offset, size // 2),
                  (size - offset - arrow_size, size // 2 - arrow_size),
                  (size - offset - arrow_size, size // 2 + arrow_size)]
    else:
        raise ValueError("Invalid direction. Choose from 'N', 'S', 'W', 'E'.")

    # Draw the arrow
    draw.polygon(points, fill=arrow_color)

    return image
