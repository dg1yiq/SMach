#
# Author: Marco Alexander Reinke (DG1YIQ)
# Date: December 2023
# License: GNU GPL 3.0
# Description: This is a simple clone of StreetMachine for the CPC 464
#

import settings as settings
import pygame as pg
import sys
import os
from map import *
from sprites import *
from player import *


class SMach:
    def __init__(self):
        pg.init()
        # Debug Mode
        self.debug = settings.DEBUG
        # Set up display
        self.zoom_factor = settings.ZOOM_FACTOR
        # Sprite Size in Pixels
        self.sprite_size = 16
        # Size of Field of View in Sprites
        self.sizex = 16
        self.sizey = 12
        # Mode of Level
        self.mode = 'day'

        # Size of the display in Pixels
        self.screen_width, self.screen_height = (self.sizex * self.sprite_size * self.zoom_factor,
                                                 self.sizey * self.sprite_size * self.zoom_factor)
        print(f"Display size: {self.screen_width} x {self.screen_height}")
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))

        # Your game clock
        self.clock = pg.time.Clock()
        self.delta_time = 1

        # Players position in the world at start in pixel coordinates on the map
        self.player_map_x = 44
        self.player_map_y = 99
        self.player_x = self.player_map_x * self.sprite_size
        self.player_y = self.player_map_y * self.sprite_size
        self.play_direction = 0
        self.player_speed = 0
        self.player_allowed = True
        self.check_allowed_area = True

        # Initialize the sprites
        self.sprites = Sprites(self, size=self.sprite_size)
        # Initialize the player
        self.player = Player(self, size=self.sprite_size)
        # Initialize the map
        self.map = Map(self)

        # Font initialization
        self.font = pg.font.Font(None, 36)

    def event_handler(self):
        delta_time = self.clock.tick(60) / 1000.0  # Calculate time elapsed since last frame in seconds

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        keys = pg.key.get_pressed()
        # Quit the game on q
        if keys[pg.K_q]:
            pg.quit()
            sys.exit()
        # Adjust player position based on keys pressed
        if keys[pg.K_LEFT]:
            self.play_direction += int(4+self.player_speed/10)
            if self.play_direction >= 360:
                self.play_direction = 0
        if keys[pg.K_RIGHT]:
            self.play_direction -= int(4+self.player_speed/10)
            if self.play_direction <= 0:
                self.play_direction = 360
        if keys[pg.K_UP]:
            if not self.player_speed < 0:
                self.player_speed += 2
            if self.player_speed >= 100:
                self.player_speed = 100
        if keys[pg.K_DOWN]:
            if (self.player_speed - 10) <= 0:
                self.player_speed = 0
            else:
                self.player_speed -= 10
            if self.player_speed == 0:
                self.player_speed = 0
            if self.player_speed < 0:
                self.player_speed = +1
        if keys[pg.K_b]:
            if self.player_speed <= 0:
                self.player_speed -= 1
            if self.player_speed <= -10:
                self.player_speed = -10
        # Debug Keys
        if self.debug:
            if keys[pg.K_a]:
                self.check_allowed_area = True
            if keys[pg.K_s]:
                self.check_allowed_area = False
            if keys[pg.K_n]:
                self.mode = 'night'
            if keys[pg.K_d]:
                self.mode = 'day'
            if keys[pg.K_w]:
                self.mode = 'winter'

    def draw(self):
        # Clear the screen fill with Backgroundcolor
        if self.mode == 'day':
            self.screen.fill(settings.BG_COLOR_DAY)
        elif self.mode == 'night':
            self.screen.fill(settings.BG_COLOR_NIGHT)
        elif self.mode == 'winter':
            self.screen.fill(settings.BG_COLOR_WINTER)

        # Calculate new player position
        self.player_x, self.player_y = self.calculate_new_position(self.player_x,
                                                                   self.player_y,
                                                                   self.player_speed,
                                                                   self.play_direction)
        # Calculate the players position on the map
        self.player_map_x = int(self.player_x // self.sprite_size)
        self.player_map_y = int(self.player_y // self.sprite_size)

        # Check if we drive over the start line
        # y=97 and x is 42,43,44 and direction is between 0 +- 90 degree
        if ((self.player_map_y == 97) and (self.player_map_x in [42, 43, 44]) and
                ((self.play_direction in range(0, 89)) or (self.play_direction in range(271, 360)))):
            print("Start")

        # Check if we are driving over the finish line
        # x=46 and y is 100,101,102 and direction is between 90 +- 90 degree
        if ((self.player_map_x == 46) and (self.player_map_y in [100, 101, 102]) and
                (self.play_direction in range(1, 179))):
            print("Finish")

        # Check if we are trying to drive over the finish line in the wrong direction
        # x=46 and y is 100,101,102 and direction is between 270 +- 90 degree
        if ((self.player_map_x == 46) and (self.player_map_y in [100, 101, 102]) and
                (self.play_direction in range(181, 359))):
            print("Wrong direction")
            self.player_x = 44 * self.sprite_size
            self.player_y = 101 * self.sprite_size
            self.play_direction = 0
            self.player_speed = 0

        # Check if Player is in allowed area
        self.player_allowed = self.player.check_allowed_area(self.player_map_x, self.player_map_y)

        # if player is not in allowed area set speed to 0
        if not self.player_allowed and self.check_allowed_area:
            if self.player_speed > 20:
                # Car was too fast... crash...
                pass
            self.player_speed = 0

        # Draw the background
        self.map.draw(self.player_x-(self.sizex//2), self.player_y-(self.sizey//2))

        # Draw Debug
        if self.debug:
            self.drawdebug()

        # Draw the player
        self.player.draw(self.play_direction)

        # Update the display
        pg.display.flip()

        # Calculate the time since the last frame
        self.delta_time = self.clock.tick(30)
        pg.display.set_caption(f'{self.clock.get_fps():.1f}')

    def drawdebug(self):
        # Draw the debug sprite
        sprite = self.map.draw_debug_sprite(self.player_map_x, self.player_map_y)
        text = self.font.render(f'Player x: {self.player_x:.1f} y:{self.player_y:.1f} '
                                f'dir:{self.play_direction:.1f} spd:{self.player_speed:.1f}', True,
                                (255, 0, 0))  # You can change the text and color here
        self.screen.blit(text, (10, 10))  # Adjust the position of the text

        text = self.font.render(f'Map x: {self.player_map_x} y:{self.player_map_y} - '
                                f'Shitf x: {int(self.player_x % self.sprites.size - 8)} '
                                f'y:{int(self.player_y % self.sprites.size - 8)} Pixel - '
                                f'Alwd: {self.player_allowed} - ChkAlwd: {self.check_allowed_area} - '
                                f'Sprite: {sprite}',
                                True, (255, 0, 0))
        self.screen.blit(text, (10, 40))

    def calculate_new_position(self, x, y, speed, direction):
        # calculate new postion for x and y out of speed and direction
        # speed is divided by 10 to get a better feeling of speed
        speed = speed / 10

        # Calculating difference in x and y direction
        dx = math.sin(math.radians(direction)) * speed
        dy = math.cos(math.radians(direction)) * speed

        # Calculating new position
        x = x - dx
        y = y - dy

        # Check if player is out of bounds
        # If so set player back to the border
        if x > self.map.mapsize_x*self.sprite_size-(self.sizex//2*self.sprite_size)-self.sprite_size:
            x = self.map.mapsize_x*self.sprite_size-(self.sizex//2*self.sprite_size)-self.sprite_size
        if x < (self.sizex//2*self.sprite_size):
            x = self.sizex//2*self.sprite_size
        if y > self.map.mapsize_y*self.sprite_size-(self.sizey//2*self.sprite_size)-self.sprite_size:
            y = self.map.mapsize_y*self.sprite_size-(self.sizey//2*self.sprite_size)-self.sprite_size
        if y < (self.sizey//2*self.sprite_size):
            y = self.sizey//2*self.sprite_size

        # Return new position
        return x, y

    # Game loop
    def mainloop(self):
        while True:
            # Handle events
            self.event_handler()

            # Draw everything
            self.draw()


if __name__ == "__main__":
    game = SMach()
    game.mainloop()