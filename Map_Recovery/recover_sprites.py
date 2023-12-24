#
# Author: Marco Alexander Reinke (DG1YIQ)
# Date: December 2023
# License: GNU GPL 3.0
# Description: This is a simple clone of StreetMachine for the CPC 464
#

from PIL import Image
import numpy as np
import sys
import os

def split_image(input_path, output_path, sprite_size):
    # Open the BMP image that we manually created from the source image
    # Original Image is from https://www.cpc-power.com/
    image = Image.open(input_path)

    # Get the dimensions of the input image
    width, height = image.size

    # Check if the image is a multiple of the sprite size
    if width % sprite_size != 0 or height % sprite_size != 0:
        print("The image is not a multiple of the sprite size")
        return

    # Calculate the number of sprites in each dimension
    num_sprites_x = width // sprite_size
    num_sprites_y = height // sprite_size

    spritestorage = []
    spritepos = 0

    map = []
    sprite_arrays = []

    # Iterate over each sprite and save it as a separate image
    for y in range(num_sprites_y):
        line = []
        for x in range(num_sprites_x):
            # Calculate the coordinates for each sprite
            left = x * sprite_size
            upper = y * sprite_size
            right = left + sprite_size
            lower = upper + sprite_size

            # Crop the image to get the sprite and convert it to RGBA
            sprite = image.crop((left, upper, right, lower))
            sprite = sprite.convert('RGBA')

            # Get the dimensions of the sprite - but should be same as sprite_size, but anyway
            width, height = sprite.size

            # Replace the green background with a transparent one
            # Loop through each pixel in the image
            for xi in range(width):
                for yi in range(height):
                    # Get the color of the current pixel
                    current_color = sprite.getpixel((xi, yi))

                    # Check if the current pixel color matches the target color
                    if current_color[:3] == (0, 101, 0):
                        # Replace the color with a transparent pixel
                        sprite.putpixel((xi, yi), (0, 0, 0, 0))

            # go trough spritestorage and check if the sprite is already in there
            # if not, add it
            if sprite not in spritestorage:
                spritepos += 1
                spritnumber = spritepos

                # Convert the sprite to a numpy array
                sprite_array = np.array(sprite)
                # Append the sprite array to our list of sprite arrays
                sprite_arrays.append(sprite_array)

                # Append the sprite pciture to our list of sprites
                spritestorage.append(sprite)
                # Save the sprite image
                sprite.save(f"{output_path}/sprite_{spritepos}.png")
                print(f"Found unique sprite No {spritepos} - saving to {output_path}/sprite_{spritepos}.png")
            else:
                # if it is, find the index of the sprite and save it as that
                spritnumber = spritestorage.index(sprite) + 1

            line.append(spritnumber)

            if spritepos > 255:
                print("Too many sprites! Max is 255")
                return
        map.append(line)
    # write map to python file
    with open(f"{output_path}/map.py", "w") as f:
        f.write(f"map = {map}")

    # generate python code for sprite_arrays and save it to file
    code = f'# This array contains {len(sprite_arrays)} sprite arrays\n'
    code += "sprites = [\n"
    for sprite_array in sprite_arrays:
        code += "    [\n"
        code += "        "
        # Iterate over the original sprite array and group RGBA values
        for i, pixel_value in enumerate(sprite_array):
            # Group RGBA values within a tuple and add a comma
            code += "["
            j = 0
            for value in enumerate(pixel_value):
                code += f"({', '.join([str(x) for x in tuple(value[1])])})"
                if not (j == sprite_size-1):
                    code += ", "
                j += 1
            code += "],\n"
            if not (i == sprite_size - 1):
                code += "        "
        code += "    ],\n"
    code += "]"  # Close the list
    with open(f"{output_path}/sprite_arrays.py", "w") as f:
        f.write(code)


if __name__ == "__main__":
    # Check if the user provided an input file
    if len(sys.argv) < 2:
        print("Please provide an input file")
        sys.exit()
    # Input Name from Commandline argument
    input_path = sys.argv[1]
    # Check if the input file exists
    if not os.path.isfile(input_path):
        print("The input file does not exist")
        sys.exit()
    output_path = "sprites"
    sprite_size = 16

    split_image(input_path, output_path, sprite_size)
