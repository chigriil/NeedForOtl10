import pygame
import sys

from Engine.apps import MicroApp
from settings import *


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

    def pretty_text_button(self, font='', text='', buttoncolor=(100, 150, 20), fontcolor=(255, 255, 255),
                           x=0, y=0, margin=5):
        """
        Рисует прямоугольник цвета buttoncolor с текстом text цвета fontcolor. Возвращает Rect прямоугольника.
        :param font: Sys.Font
        :param text: str
        :param buttoncolor:
        :param fontcolor:
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


