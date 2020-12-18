import pygame
import sys
from random import choice

import pygame

from Engine.apps import MicroApp
from Engine.utils.utils import load_music_from_folder
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SONG_END, menu_music_path, menu_music_volume
from src.game import Game


class InputBox:
    """
    Class creating a name writing box.
    """

    def __init__(self, screen, x=0, y=0, w=0, h=0, text=''):
        self.screen = screen
        self.name_recorded = False
        self.name = ''
        self.username = ''
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (255, 255, 255)  # The non-active color
        self.font = pygame.font.SysFont('arial', 40)
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
            if self.rect.collidepoint(event.pos):
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
        width = max(self.rect.w, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self):
        """
        A procedure to display the text on the screen.
        :object screen: pygame.Surface
        :return: None
        """
        # Blit the text.
        self.screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(self.screen, self.color, self.rect, 2)

    def run(self):
        for event in pygame.event.get():
            self.draw()
            self.handle_event(event)
            # Checks for the end of writing
            if self.name_recorded:
                self.username = self.name
            self.update()


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


menu_music = load_music_from_folder(menu_music_path)
pygame.mixer.music.set_endevent(SONG_END)


def next_song():
    pygame.mixer.music.unload()
    pygame.mixer.music.load(choice(menu_music))
    pygame.mixer.music.play()


class MainMenu(Menu):
    def __init__(self, screen, clock):
        super(MainMenu, self).__init__(screen, clock)
        self.FPS = 10
        self.customisationmenu = CustomisationMenu(self.screen, self.clock)
        self.fontcolor = (255, 255, 255)
        self.buttoncolor = (15, 29, 219)
        self.font = pygame.font.SysFont('Comic Sans MS', int(70 / 900 * self.screen_height))
        self.titlefont = pygame.font.SysFont('ariel', int(300 / 900 * self.screen_height))

        pygame.mixer.music.set_volume(menu_music_volume)
        next_song()

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

    def on_iteration(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == SONG_END:
                next_song()

            if event.type == pygame.MOUSEBUTTONDOWN and \
                    self.pretty_text_button(self.font, "Выход", self.buttoncolor, self.fontcolor,
                                            self.screen_width // 2,
                                            self.screen_height * 9 // 12).collidepoint(event.pos):
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and \
                    self.pretty_text_button(self.font, "Начать", self.buttoncolor, self.fontcolor,
                                            self.screen_width // 2,
                                            self.screen_height * 6 // 12).collidepoint(event.pos):  # Кнопка Начала
                self.customisationmenu.run()

        self.draw()
        self.clock.tick(self.FPS)
        pygame.display.flip()


class LeaderBoard(Menu):
    def __init__(self, screen, clock):
        super(LeaderBoard, self).__init__(screen, clock)
        self.FPS = 10
        self.fontcolor = (255, 255, 255)
        self.buttoncolor = (15, 29, 219)
        self.font = pygame.font.SysFont('Comic Sans MS', 50 / 900 * self.screen_height)

    def run_once(self):
        self.screen.fill(self.background_color)
        self.pretty_text_button(self.font, "Обратно в меню",
                                self.buttoncolor,
                                self.fontcolor,
                                self.screen_width // 2,
                                self.screen_height * 7 // 12)
        pygame.display.flip()

    def loader(self):
        pass

    def updater(self):
        pass

    def on_iteration(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == SONG_END:
                next_song()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.pretty_text_button(self.font, "Обратно в меню",
                                           self.buttoncolor,
                                           self.fontcolor,
                                           self.screen_width // 2,
                                           self.screen_height * 7 // 12).collidepoint(event.pos):
                    self.active = False


class CustomisationMenu(Menu):
    def __init__(self, screen, clock):
        super(CustomisationMenu, self).__init__(screen, clock)
        self.FPS = 30
        self.fontcolor = (255, 255, 255)
        self.buttoncolor = (15, 29, 219)
        self.font = pygame.font.SysFont('Comic Sans MS', int(50 / 900 * self.screen_height))
        self.titlefont = pygame.font.SysFont('ariel', int(100 / 900 * self.screen_height))
        self.name_input = InputBox(self.screen,
                                   self.screen_width * 1 // 2 - 500 // 2,
                                   self.screen_height * 9 // 24 - 50 // 2,
                                   500, 50)

    def draw(self):
        self.screen.fill(self.background_color)

        self.pretty_text_button(self.font, "Меню кастомизации", self.buttoncolor, self.fontcolor,
                                self.screen_width // 2, self.screen_height * 3 // 12)

        self.pretty_text_button(self.font, "Начать игру", self.buttoncolor, self.fontcolor,
                                self.screen_width // 2, self.screen_height * 7 // 12)
        if self.name_input.name_recorded:
            self.pretty_text_button(self.font, 'Имя записано', self.buttoncolor, self.fontcolor,
                                    self.screen_width // 2, self.screen_height * 9 // 12)
        else:
            self.pretty_text_button(self.font, 'Введите имя и нажмите enter', self.buttoncolor, self.fontcolor,
                                    self.screen_width // 2, self.screen_height * 9 // 12)

    def on_iteration(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.pretty_text_button(self.font, "Начать игру",
                                           self.buttoncolor,
                                           self.fontcolor,
                                           self.screen_width // 2,
                                           self.screen_height * 7 // 12).collidepoint(event.pos) and \
                        self.name_input.name_recorded:
                    self.alive = False

            self.name_input.handle_event(event)
            # Checks for the end of writing
            if self.name_input.name_recorded:
                self.name_input.username = self.name_input.name
            self.name_input.update()

        self.draw()
        self.name_input.draw()
        self.clock.tick(self.FPS)
        pygame.display.flip()

    def atexit(self):
        return Game(self.screen, self.clock, self.name_input.username).run()
