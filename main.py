"""
Pygame не сильно быстро рисует, пэтому оптимизация рисования важна
Возможно стоит сделать многопоточную программу (типо io рисования операция не сверх медленная, но и не быстрая)
TODO: прикрутить режим разработчика
TODO: добавить анотации типов везде, или в .pyi файлы (точнее зашарить за модуль typing)
TODO: сделать редактор уровней (ну это после прописания класса уровня, обработки игровых событий и т.д.)
TODO: Пайгейм медленно рисует, плэтому разрешение спрайтов поменьше + их рисовать в bmp или в png (никакого jpg)
"""
import sys

import numpy as np
import pygame

from Engine.apps import MicroApp, App, LoadingScreen, Init
from Engine.camera import Camera
from Levels.testlevel import TestLevel
from settings import *

pygame.font.init()
pygame.mixer.pre_init()
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

DEVMODE = True


class Game(MicroApp):
    def __init__(self, screen, clock):
        super(Game, self).__init__(screen, clock, lifetime=float('inf'))
        self.FPS = 0
        self.scene = TestLevel(Game)
        self.camera = Camera(self.screen)
        self.camera.start()

    def draw(self):
        self.scene.draw(self.camera)
        self.camera.show()
        pygame.display.update()

    def step(self, dt):
        self.scene.step(dt)

    def on_iteration(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed(3)[0]:
                self.camera.position += np.array(event.rel) * [-1, 1] / self.camera.scale_factor
            if event.type == pygame.MOUSEWHEEL:
                self.camera.distance -= event.y
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_F3]:
                    global DEVMODE
                    DEVMODE = not DEVMODE
        self.run_tasks()
        self.step(self.clock.get_time() / 1000)
        self.draw()
        self.clock.tick(self.FPS)
        pygame.display.set_caption('{:.1f}'.format(self.clock.get_fps()))  # Вывод фпс в заголовок окна


app = App(micro_apps=[Init(screen, clock), LoadingScreen(screen, clock, lifetime=3), Game(screen, clock)])
app.run()
