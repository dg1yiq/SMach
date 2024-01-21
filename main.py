#
# Author: Marco Alexander Reinke (DG1YIQ)
# Date: December 2023
# License: GNU GPL 3.0
# Description: This is a simple clone of StreetMachine for the CPC 464
#
# Todo: geht noch nicht: python -m PyInstaller --add-data="files/highscore.png:files" main.py
#

import settings as settings
import pygame as pg
import sys
import os
from map import *
from sprites import *
from player import *
from highscore import *


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
        self.mode = 'highscore'

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

        # Player direction and speed
        self.player_direction = 0
        self.player_speed = 0

        # Player is an allowed area (street or green area)
        self.player_allowed = True

        # Activate Check if player is in allowed area
        self.check_allowed_area = True

        # Player start and end time
        self.player_starttime = 0
        self.player_endtime = 0
        self.player_time_running = False

        # Player Car Damage
        self.player_damage = 0

        # Player Time for Day, Night and Winter
        self.player_time_day = 0
        self.player_time_night = 0
        self.player_time_winter = 0

        # Initialize the sprites
        self.sprites = Sprites(self, size=self.sprite_size)
        # Initialize the player
        self.player = Player(self, size=self.sprite_size)
        # Initialize the map
        self.map = Map(self)
        # Initialize the highscore
        self.highscore = Highscore(self)

        # Font initialization
        self.font_small = pg.font.Font(None, 36)
        self.font_big = pg.font.Font(None, 100)
        self.font_normal = pg.font.Font(None, 55)

    def event_handler(self):
        # Handle events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        # Get pressed keys
        keys = pg.key.get_pressed()

        # Quit the game on q
        if keys[pg.K_q]:
            pg.quit()
            sys.exit()

        if keys[pg.K_ESCAPE] and (self.mode == 'day' or self.mode == 'night' or self.mode == 'winter'):
            self.mode = 'highscore'
            self.player_speed = 0

        if keys[pg.K_SPACE] and self.mode == 'highscore':
            self.player_starttime = 0
            self.player_endtime = 0
            self.mode = 'day'

        if self.mode != 'highscore':
            # Adjust player position based on keys pressed
            if keys[pg.K_LEFT]:
                self.player_direction += int(4+self.player_speed/10)
                if self.player_direction >= 360:
                    self.player_direction = 0
            if keys[pg.K_RIGHT]:
                self.player_direction -= int(4+self.player_speed/10)
                if self.player_direction <= 0:
                    self.player_direction = 360
            # Accelerate and break
            if keys[pg.K_UP]:
                if not self.player_speed < 0:
                    self.player_speed += 2
                # Limit Speed to 30 if car is damaged more than 75 %
                if self.player_speed >= 30 and self.player_damage > 75:
                    self.player_speed = 30
                # Limits Speed to 100 in general
                if self.player_speed >= 100:
                    self.player_speed = 100
            if keys[pg.K_DOWN]:
                if (self.player_speed - 5) <= 0:
                    self.player_speed = 0
                else:
                    self.player_speed -= 5
                if self.player_speed == 0:
                    self.player_speed = 0
                if self.player_speed < 0:
                    self.player_speed = +1
            # Backwards only when standing still
            if keys[pg.K_b]:
                if self.player_speed <= 0:
                    self.player_speed -= 1
                if self.player_speed <= -10:
                    self.player_speed = -10

            # Debug Keys
            if self.debug:
                # Enable or disable Position Check (so we can go everywhere)
                if keys[pg.K_a]:
                    self.check_allowed_area = True
                if keys[pg.K_s]:
                    self.check_allowed_area = False
                # Flip between day, night and winter level
                if keys[pg.K_n]:
                    self.mode = 'night'
                    self.sprites.load_sprites()
                if keys[pg.K_d]:
                    self.mode = 'day'
                    self.sprites.load_sprites()
                if keys[pg.K_w]:
                    self.mode = 'winter'
                    self.sprites.load_sprites()
                # Reset Player Damage
                if keys[pg.K_r]:
                    self.player_damage = 0

    def draw_game(self):
        # Clear the screen fill with Background color
        if self.mode == 'day':
            self.screen.fill(settings.BG_COLOR_DAY)
        elif self.mode == 'night':
            self.screen.fill(settings.BG_COLOR_NIGHT)
        elif self.mode == 'winter':
            self.screen.fill(settings.BG_COLOR_WINTER)

        # Draw the background
        self.map.draw(self.player_x-(self.sizex//2), self.player_y-(self.sizey//2))

        # Draw Debug
        if self.debug:
            # Draw the debug sprite
            sprite = self.map.draw_debug_sprite(self.player_map_x, self.player_map_y)
            # Draw the debug text
            text = self.font_small.render(f'Player x: {self.player_x:.1f} y:{self.player_y:.1f} '
                                          f'dir:{self.player_direction:.1f} spd:{self.player_speed:.1f} '
                                          f'dmg: {self.player_damage}', True,
                                          (255, 0, 0))  # You can change the text and color here
            self.screen.blit(text, (10, 10))  # Adjust the position of the text

            text = self.font_small.render(f'Map x: {self.player_map_x} y:{self.player_map_y} - '
                                          f'Shitf x: {int(self.player_x % self.sprites.size - 8)} '
                                          f'y:{int(self.player_y % self.sprites.size - 8)} Pixel - '
                                          f'Alwd: {self.player_allowed} - ChkAlwd: {self.check_allowed_area}',
                                          True, (255, 0, 0))
            self.screen.blit(text, (10, 40))

        # Draw the Timewatch
        text = self.font_small.render(f'{self.formattime(self.player_starttime, self.player_endtime)}',
                                      True, (255, 0, 0))
        self.screen.blit(text, (10, self.screen_height-40))

        # Dram the Damage Level as yellow bar in an red rectangle - range 0-100
        text = self.font_small.render(f'Damage', True, (255, 0, 0))
        self.screen.blit(text, (800, self.screen_height - 40))
        pg.draw.rect(self.screen, (255, 255, 0), (910, self.screen_height-38, self.player_damage, 20))
        pg.draw.rect(self.screen, (255, 0, 0), (910, self.screen_height - 38, 100, 20), 2)

        # Draw the player
        self.player.draw(self.player_direction)

        # Update the display
        pg.display.flip()

        # Calculate the time since the last frame
        self.delta_time = self.clock.tick(30)
        pg.display.set_caption(f'Street Machine - {self.clock.get_fps():.1f} fps')

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

    def formattime(self, starttime, endtime):
        ticks = endtime - starttime
        millis = int(ticks) % 100
        seconds = int(ticks / 1000 % 60)
        minutes = int(ticks / 60000 % 24)

        return f'{minutes:02d}:{seconds:02d}:{millis:02d}'

    # Game loop
    def mainloop(self):
        while True:
            # Handle events
            self.event_handler()

            if self.mode == 'highscore':
                self.highscore.draw()
            elif self.mode == 'day' or self.mode == 'night' or self.mode == 'winter':
                # Draw everything
                self.draw_game()

            ticks = pg.time.get_ticks()
            if self.player_time_running:
                self.player_endtime = ticks

            # Calculate new player position
            self.player_x, self.player_y = self.calculate_new_position(self.player_x,
                                                                       self.player_y,
                                                                       self.player_speed,
                                                                       self.player_direction)
            # Calculate the players position on the map
            self.player_map_x = int(self.player_x // self.sprite_size)
            self.player_map_y = int(self.player_y // self.sprite_size)

            # Check if we drive over the start line
            # y=97 and x is 42,43,44 and direction is between 0 +- 90 degree
            if ((self.player_map_y == 97) and (self.player_map_x in [42, 43, 44]) and
                    ((self.player_direction in range(0, 89)) or (self.player_direction in range(271, 360)))
                    and not self.player_time_running):
                self.player_time_running = True
                self.player_starttime = ticks
                self.player_endtime = ticks

            # Check if we are driving over the finish line
            # x=46 and y is 100,101,102 and direction is between 90 +- 90 degree
            if ((self.player_map_x == 46) and (self.player_map_y in [100, 101, 102]) and
                    (self.player_direction in range(1, 179)) and self.player_time_running):
                self.player_time_running = False
                self.player_endtime = ticks
                self.player_x = 44 * self.sprite_size
                self.player_y = 99 * self.sprite_size
                self.player_direction = 0
                self.player_speed = 0
                self.player_damage = 0
                if self.mode == 'day':
                    self.player_time_day = self.player_endtime - self.player_starttime
                    self.mode = 'night'
                    self.sprites.load_sprites()
                elif self.mode == 'night':
                    self.player_time_night = self.player_endtime - self.player_starttime
                    self.mode = 'winter'
                    self.sprites.load_sprites()
                elif self.mode == 'winter':
                    self.player_time_winter = self.player_endtime - self.player_starttime
                    self.sprites.load_sprites()
                    self.highscore.ask_for_name((self.player_time_day +
                                                 self.player_time_night +
                                                 self.player_time_winter) / 3)
                    self.mode = 'highscore'

            # Check if we are trying to drive over the finish line in the wrong direction
            # x=46 and y is 100,101,102 and direction is between 270 +- 90 degree
            if ((self.player_map_x == 46) and (self.player_map_y in [100, 101, 102]) and
                    (self.player_direction in range(181, 359))):
                self.player_x = 44 * self.sprite_size
                self.player_y = 101 * self.sprite_size
                self.player_speed = 0

            # Check if Player is in allowed area
            self.player_allowed = self.player.check_allowed_area(self.player_map_x, self.player_map_y)

            # if player is not in allowed area set damag level and set speed to 0
            if not self.player_allowed and self.check_allowed_area:
                if self.player_speed > 20:
                    self.player_damage += self.player_speed * 1.5
                    # Car was too fast... crash...
                    if self.player_damage > 100:
                        self.player_damage = 100
                        self.player_speed = 0
                        # Todo - Car Repair
                self.player_speed = 0


if __name__ == "__main__":
    game = SMach()
    game.mainloop()
