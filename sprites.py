#
# Author: Marco Alexander Reinke (DG1YIQ)
# Date: December 2023
# License: GNU GPL 3.0
# Description: This is a simple clone of StreetMachine for the CPC 464
#

import pygame as pg
import os


class Sprites:
    def __init__(self, game, size=16, usefiles=False):
        self.game = game
        # Directory containing your sprite images
        self.sprites_directory = "sprites/"
        # Size of your sprites in Pixels
        self.size = size
        # List to store loaded sprite images
        self.images = None
        self.usefiles = usefiles
        self.color = None

        # Import the sprite array from sprites_array.py
        from sprites_array import sprites
        self.sprites = sprites

        # Load the sprites
        self.load_sprites()

    def load_sprites(self):
        from sprites_array import summer_color, winter_color, night_color
        self.images = []
        # Load the sprites from PNG Files or from sprites_array.py
        if self.usefiles:
            self.load_sprite_from_files()
        else:
            # Create the sprite images
            # Iterate over the sprite array
            print(self.game.mode)
            if self.game.mode == "day":
                self.color = summer_color
            elif self.game.mode == "winter":
                self.color = winter_color
            elif self.game.mode == "night":
                self.color = night_color
            else:
                self.color = summer_color
            for sprite_array in self.sprites:
                sprite_surface = self.create_sprite_image(sprite_array, self.color, self.size)
                self.images.append(sprite_surface)

    def load_sprite_from_files(self):
        # Iterate over the range of sprite indices (1 to 126 in your case)
        for i in range(1, 127):
            # Generate the file path based on the naming pattern
            sprite_path = os.path.join(self.sprites_directory, f"sprite_{i}.png")

            # Load and append the sprite image to the list
            self.images.append(pg.image.load(sprite_path).convert_alpha())

    def create_sprite_image(self, sprite_array, color, sprite_size):
        # Create a new surface with the correct dimensions and transparency
        surface = pg.Surface((sprite_size, sprite_size), pg.SRCALPHA)
        # Iterate over the sprite array
        for y, row in enumerate(sprite_array):
            for x, pixel in enumerate(row):
                finalpixel = color[pixel[0]] + (pixel[1],)
                surface.set_at((x, y), finalpixel)
        return surface
