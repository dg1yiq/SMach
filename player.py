#
# Author: Marco Alexander Reinke (DG1YIQ)
# Date: December 2023
# License: GNU GPL 3.0
# Description: This is a simple clone of StreetMachine for the CPC 464
#

import pygame as pg
import os


class Player:
    def __init__(self, game, size=16, usefiles=False):
        self.game = game
        # Directory containing your sprite images
        self.sprites_directory = "sprites/"
        # Size of your sprites in Pixels
        self.sprite_size = size
        self.usefiles = usefiles
        self.player_sprite = None

        self.allowed_sprites = [49, 50, 51, 52, 53, 55, 56, 57, 58, 59, 60, 63, 64, 66, 68, 69, 70, 71, 72,
                                75, 76, 85, 99, 123, 3]

        # Load the player sprite from PNG File or from sprites_array.py
        if self.usefiles:
            self.player_sprite = self.load_sprite_from_file()
        else:
            # Import the sprite array from sprites_array.py
            from sprites_array import player_sprite
            from sprites_array import summer_color
            self.player_sprite = pg.transform.scale(self.create_sprite_image(player_sprite,
                                                                             summer_color,
                                                                             self.sprite_size),
                                                    (self.sprite_size * self.game.zoom_factor,
                                                     self.sprite_size * self.game.zoom_factor))

    def load_sprite_from_file(self):
        sprite_path = os.path.join(self.sprites_directory, f"player.png")
        player_sprite = pg.transform.scale(pg.image.load(sprite_path).convert_alpha(),
                                           (self.sprite_size * self.game.zoom_factor,
                                            self.sprite_size * self.game.zoom_factor))
        return player_sprite

    def draw(self, direction):
        # Draw the player in the center
        rotated_player = pg.transform.rotate(self.player_sprite, direction)
        player_rect = rotated_player.get_rect(center=(self.game.screen_width // 2, self.game.screen_height // 2))
        self.game.screen.blit(rotated_player, player_rect.topleft)

    def create_sprite_image(self, sprite_array, color, sprite_size):
        # Create a new surface with the correct dimensions and transparency
        surface = pg.Surface((sprite_size, sprite_size), pg.SRCALPHA)
        # Iterate over the sprite array
        for y, row in enumerate(sprite_array):
            for x, pixel in enumerate(row):
                finalpixel = color[pixel[0]] + (pixel[1],)
                surface.set_at((x, y), finalpixel)
        return surface

    def check_allowed_area(self, x, y):
        if self.game.map.map_data[y][x] in self.allowed_sprites:
            return True
        else:
            return False
