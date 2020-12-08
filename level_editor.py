"""
Редактор уровней

Задание фона уровня:
Написать в консоль background_adress = *название пикчи*
!!!Пикча должна лежать в папке background_pics!!!

Создание границы уровня:
Зажать Y
ЛКМ - первая точка границы уровня
ПКМ - вторая точка границы уровня
Отжать Y - граница сохраняется

Размещение объектов
Нажать O
В консоль (если будет не лень, то и куда-то в само окне pygame)
будет выведено название объекта
Стрелка вправо - следующий объект
Стрелка влево - *WOW, HOW  CAN IT BE????* предыдущий объект
Нажать ЛКМ - разместить объект
Нажать O - выйти из режима размещения объектов

Размещение персонажей
Нажать P
В консоль (если будет не лень, то и куда-то в само окне pygame)
будет выведено название персонажа
Стрелка вправо - следующий персонаж
Стрелка влево - *WOW, HOW  CAN IT BE????* предыдущий персонаж
Нажать ЛКМ - разместить персонажа
Нажать P - выйти из режима размещения персонажей

Убрать последний созданный объект
CTRL + Z

"""

import sys

import numpy as np
import pygame

import Engine.__dark_magic__ as dark_magic
from Engine.apps import App
from Engine.apps import MicroApp
from Engine.camera import Camera
from Engine.overlays import FPS
from settings import *
from src.Levels.testlevel import TestLevel
from src.game import Game

if sys.hexversion < 0x30900f0:
    raise SystemError("Даня, я знаю это ты. Установи питон 3.9.0 или выше")
dark_magic.init()
pygame.mixer.pre_init()
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

saveTester = TestLevel(Game)
saveTester.primary_init()
saveTester.save_level('pizda')


class LevelEditor(MicroApp):
    def __init__(self, screen, clock):
        super(LevelEditor, self).__init__(screen, clock, lifetime=float('inf'))
        self.FPS = 0
        self.scene = TestLevel(Game)
        self.scene.load_level('pizda')
        self.camera = Camera(self.screen, distance=16)
        self.camera.start()

        self.overlays = [FPS(self.screen, self.clock)]

        self.DEVMODE = DEVMODE

    def draw(self):
        self.camera.view(self.scene)

        if self.DEVMODE:
            self.camera.devview(self.scene)

        self.camera.show(self.DEVMODE)

        for overlay in self.overlays:
            overlay.draw()

        pygame.display.update()

    def step(self, dt):
        for overlay in self.overlays:
            overlay.update(dt)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.atexit()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed(3)[0]:
                self.camera.position += np.array(event.rel) * [-1, 1] / self.camera.scale_factor
            if event.type == pygame.MOUSEWHEEL:
                self.camera.distance -= event.y
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_r]:
                    self.camera.position = 0, 0
                    self.camera.distance = 14
                if pygame.key.get_pressed()[pygame.K_F3]:
                    self.DEVMODE = not self.DEVMODE

    def atexit(self):
        """
        Действия при выходе из приложения
        :return: следущеее приложение, которое запустится сразу или None, если не предусмотрено следущее
        """
        self.scene.save_level()


if __name__ == '__main__':
    app = App(micro_apps=[LevelEditor(screen, clock)])
    app.run()
