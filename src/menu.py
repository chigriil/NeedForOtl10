import pygame
import sys

from Engine.apps import MicroApp
from settings import *
from src.game import Game


class InputBox:
    """
    Class creating a name writing box.
    """

    def __init__(self, x=0, y=0, w=0, h=0, text=''):
        self.name_recorded = False
        self.name = ''
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (255, 255, 255)  # The non-active color
        self.font = pygame.font.SysFont('arial', 50)
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.active = False

    def handle_event(self, event):
        """
        The thing that handles the events like writing and deactivating the inputbox.
        :param event:
        :return:
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos[0], event.pos[1]):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = (100, 100, 100) if self.active else (255, 255, 255)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.name = self.text
                    self.name_recorded = True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self):
        """
        A procedure to update the size of the inputbox.
        :return: None
        """
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        """
        A procedure to display the text on the screen.
        :object screen: pygame.Surface
        :return: None
        """
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Menu(MicroApp):
    def __init__(self, screen, clock):
        super(Menu, self).__init__(screen, clock, lifetime=float('inf'))
        self.FPS = 0
        self.username = ''
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.background_color = (0, 0, 0)

        self.fontcolor = (0, 0, 0)
        self.font = pygame.font.SysFont('Comic Sans MS', 50)

    def pretty_text_button(self, font=None, text='', buttoncolor=(100, 150, 20), fontcolor=(255, 255, 255),
                           x=0, y=0, margin=5):
        """
        Рисует прямоугольник цвета buttoncolor с текстом text цвета fontcolor. Возвращает Rect прямоугольника.
        :param font: Sys.Font
        :param text: str
        :param buttoncolor: tuple
        :param fontcolor: tuple
        :param x: int
        :param y: int
        :param margin: int
        :return: Rect
        """
        text_surface = font.render(text, True, fontcolor)
        x, y = x - text_surface.get_width() // 2 - margin, y - text_surface.get_height() // 2 - margin
        pygame.draw.rect(self.screen, buttoncolor, pygame.Rect((x, y), (text_surface.get_width() + 2 * margin,
                                                                        text_surface.get_height() + 2 * margin)))
        self.screen.blit(text_surface, (x + margin, y + margin))
        return pygame.Rect((x, y), (text_surface.get_width() + 2 * margin, text_surface.get_height() + 2 * margin))


class MainMenu(Menu):
    def __init__(self, screen, clock):
        super(MainMenu, self).__init__(screen, clock)
        self.FPS = 10
        self.leaderboard_on = False
        self.fontcolor = (255, 255, 255)
        self.buttoncolor = (15, 29, 219)
        self.font = pygame.font.SysFont('Comic Sans MS', 100)
        self.titlefont = pygame.font.SysFont('ariel', 300)

        self.leaderboard_background_color = (0, 0, 0)

    def draw(self):
        self.screen.fill(self.background_color)

        self.pretty_text_button(self.titlefont, "Need for Otl(10)", self.buttoncolor, self.fontcolor,
                                self.screen_width // 2, self.screen_height // 7)
        self.pretty_text_button(self.font, "Выжившие", self.buttoncolor, self.fontcolor,
                                self.screen_width // 2, self.screen_height * 5 // 12)
        self.pretty_text_button(self.font, "Начать", self.buttoncolor, self.fontcolor,
                                self.screen_width // 2, self.screen_height * 7 // 12)
        self.pretty_text_button(self.font, "Выход", self.buttoncolor, self.fontcolor,
                                self.screen_width // 2, self.screen_height * 9 // 12)

    def draw_leaderboard(self):
        self.screen.fill(self.leaderboard_background_color)
        pass

    def on_iteration(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and \
                    self.pretty_text_button(self.font, "Выход", self.buttoncolor, self.fontcolor,
                                            self.screen_width // 2,
                                            self.screen_height * 9 // 12).collidepoint(event.pos):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and \
                    self.pretty_text_button(self.font, "Выжившие", self.buttoncolor, self.fontcolor,
                                            self.screen_width // 2,
                                            self.screen_height * 5 // 12).collidepoint(event.pos):  # Кнопка Выжившие
                self.leaderboard_on = not self.leaderboard_on
            if event.type == pygame.MOUSEBUTTONDOWN and \
                    self.pretty_text_button(self.font, "Начать", self.buttoncolor, self.fontcolor,
                                            self.screen_width // 2, self.screen_height * 7 // 12).collidepoint(
                        event.pos):  # Кнопка Начала
                self.alive = False
            if self.leaderboard_on:
                self.screen.fill((255, 255, 255))
            else:
                self.draw()
        self.clock.tick(self.FPS)
        pygame.display.flip()

    def atexit(self):
        return CustomisationMenu(self.screen, self.clock).run()


class CustomisationMenu(Menu):
    def __init__(self, screen, clock):
        super(CustomisationMenu, self).__init__(screen, clock)
        self.FPS = 10
        self.fontcolor = (255, 255, 255)
        self.buttoncolor = (15, 29, 219)

        self.font = pygame.font.SysFont('Comic Sans MS', 50)
        self.titlefont = pygame.font.SysFont('ariel', 100)

        self.name_input = InputBox(self.screen_width * 4 // 12 - 500 // 2,
                                   self.screen_height * 3 // 24 - 50 // 2, 500, 50)

    def draw(self):
        self.screen.fill(self.background_color)

        self.name_input.draw(self.screen)

    def on_iteration(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.alive = False
        self.draw()
        self.clock.tick(self.FPS)
        pygame.display.flip()

    def atexit(self):
        return Game(self.screen, self.clock).run()


class GameMenu(Menu):
    def __init__(self, screen, clock):
        super(GameMenu, self).__init__(screen, clock)
        self.FPS = 10
        self.background_color = (0, 0, 0)
        self.fontcolor = (255, 255, 255)
        self.buttoncolor = (15, 29, 219)

        self.font = pygame.font.SysFont('Comic Sans MS', 50)

    def draw(self):
        self.screen.fill(self.background_color)

        self.pretty_text_button(self.font, "Выход", self.buttoncolor, self.fontcolor,
                                self.screen_width // 2, self.screen_height * 9 // 12)

    def on_iteration(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                self.alive = False
            if event.type == pygame.MOUSEBUTTONDOWN and \
                    self.pretty_text_button(self.font, "Выход", self.buttoncolor, self.fontcolor,
                                            self.screen_width // 2,
                                            self.screen_height * 9 // 12).collidepoint(event.pos):
                pygame.quit()
                sys.exit()
        self.draw()
        self.clock.tick(self.FPS)
        pygame.display.flip()

