import pygame as pg
import ast


class Highscore:
    def __init__(self, game):
        self.game = game
        self.highscore = []
        self.highscore_max = 9
        self.highscore_file = "highscore.txt"
        self.load_highscore()

    def load_highscore(self):
        try:
            with open(self.highscore_file, "r") as file:
                self.highscore = test = ast.literal_eval(file.read())
        except FileNotFoundError:
            self.highscore = [["---", 600000] for i in range(0, self.highscore_max)]

    def save_highscore(self):
        with open(self.highscore_file, "w") as file:
            file.write(str(self.highscore))

    def ask_for_name(self, score):

        input_box = pg.Rect(300, 250, 200, 40)
        color_inactive = pg.Color('lightskyblue3')
        color_active = pg.Color('dodgerblue2')
        color = color_inactive
        text = ''
        active = False
        font = pg.font.Font(None, 36)

        running = True
        while (running):
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pg.KEYDOWN:
                    if active:
                        if event.key == pg.K_RETURN:
                            running = False
                        elif event.key == pg.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            # Render the input box
            image = pg.image.load("highscore.png")
            self.game.screen.blit(image, (0, 0))
            pg.draw.rect(self.game.screen, color, input_box, 2)
            txt_surface = font.render(text, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            self.game.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

            pg.display.flip()

        # Add the player to the highscore list
        self.highscore.append([text, score])
        # Sort the highscore list by score
        self.highscore.sort(key=lambda x: x[1])
        # Remove the last entry
        self.highscore.pop()
        # Save the highscore
        self.save_highscore()

    def draw(self):
        # Draw an Image "highscore.png" in the middle of the screen as background
        image = pg.image.load("highscore.png")
        self.game.screen.blit(image, (0, 0))

        # Calculate the time since the last frame
        self.game.delta_time = self.game.clock.tick(30)
        pg.display.set_caption(f'Street Machine - {self.game.clock.get_fps():.1f} fps')

        # Draw "Highscore" Text
        text = self.game.font_big.render(f'Highscore', True, (255, 255, 0))
        self.game.screen.blit(text, (self.game.screen_width // 2 - 150, 50))

        # Draw the Highscore
        for i in range(0, self.highscore_max):
            text = self.game.font_normal.render(f'{i + 1}. {self.highscore[i][0]}', True,
                                           (255, 255, 0))
            self.game.screen.blit(text, (self.game.screen_width // 2 - 400, 150 + i * 50))

            text = self.game.font_normal.render(f'{self.game.formattime(0, self.highscore[i][1])}', True,
                                           (255, 255, 0))
            self.game.screen.blit(text, (self.game.screen_width // 2 + 200, 150 + i * 50))

        # Draw "Press Space to Start" Text
        text = self.game.font_small.render(f'Press Space to Start', True, (255, 255, 0))
        self.game.screen.blit(text, (self.game.screen_width // 2 - 150, self.game.screen_height - 50))

        # Update the display
        pg.display.flip()