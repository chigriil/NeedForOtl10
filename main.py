"""
Pygame не сильно быстро рисует, пэтому оптимизация рисования важна
Возможно стоит сделать многопоточную программу (типо io рисования операция не сверх медленная, но и не быстрая)
TODO: добавить анотации типов везде, или в .pyi файлы (точнее зашарить за модуль typing)
TODO: сделать редактор уровней (ну это после прописания класса уровня, обработки игровых событий и т.д.)
TODO: Пайгейм медленно рисует, плэтому разрешение спрайтов поменьше + их рисовать в bmp или в png (никакого jpg)
"""

import sys

import pygame

from Engine.apps import App, Init
from settings import *
from src.game import Game, LoadingScreen

if sys.hexversion < 0x30900f0:
    raise SystemError("Даня, я знаю это ты. Установи питон 3.9.0 или выше")

pygame.font.init()
pygame.mixer.pre_init()
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

app = App(micro_apps=[Init(screen, clock), LoadingScreen(screen, clock, lifetime=0), Game(screen, clock)])
app.run()
