import pygame

from Engine.apps import App
from settings import *
from src.game import Game

pygame.mixer.pre_init()
pygame.mixer.init()
pygame.init()
pygame.font.init()
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

app = App(micro_apps=[Game(screen, clock, 'dev_level')])
app.run()
