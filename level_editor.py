"""
Редактор уровней

переключение между режимами - стрелки вверх и вниз

Задание фона уровня:
bg_select
Выбор бэкграунда стрелками
Вправо - след бг
Влево - пред бг

Создание границы уровня:
border_placer
ЛКМ - первая точка границы уровня
ПКМ - вторая точка границы уровня
Нажать S - граница сохраняется

Размещение объектов
object_placer
В консоль (если будет не лень, то и куда-то в само окне pygame)
будет выведено название объекта
Стрелка вправо - следующий объект
Стрелка влево - *WOW, HOW  CAN IT BE????* предыдущий объект
Нажать ЛКМ - разместить объект

Изначально помещаются  статичные объекты, изменить режим - нажать O



Размещение персонажей
entity_placer
В консоль (если будет не лень, то и куда-то в само окне pygame)
будет выведено название персонажа
Стрелка вправо - следующий персонаж
Стрелка влево - *WOW, HOW  CAN IT BE????* предыдущий персонаж
Нажать ЛКМ - разместить персонажа

Сохранение уровня в файл
Нажать C

Убрать последний созданный объект
CTRL + Z

"""

import sys

import numpy as np
import pygame
import pymunk

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




class LevelEditor(MicroApp):
    """
    Собсна, редактор уровней
    """
    def __init__(self, screen, clock):
        super(LevelEditor, self).__init__(screen, clock, lifetime=float('inf'))
        self.FPS = 0
        self.scene = TestLevel(Game)
        self.scene.load_level('default_level')
        self.camera = Camera(self.screen, distance=16)
        self.camera.start()

        self.overlays = [FPS(self.screen, self.clock)]

        self.DEVMODE = DEVMODE
        self.modes = ['bg_select', 'border_placer', 'object_placer', 'entity_placer', 'camera_motion']
        self.mode_number = 0
        self.objects = ['fridge', 'closet', 'alarm', 'mouse']
        self.placeable_objects = {'fridge': {'height': 1, 'width': 1, 'sprite_adress': 'Resources/pictures/holodos.png',
                                        'shape': 'rect'},
                            'closet': {'height': 1, 'width': 1, 'sprite_adress': 'Resources/pictures/closet.png',
                                        'shape': 'rect'},
                             'alarm': {'height': 1, 'radius': 1, 'sprite_adress': 'Resources/pictures/alarm.png',
                                        'shape': 'circle'},
                             'mouse': {'height': 1, 'width': 1, 'sprite_adress': 'Resources/pictures/mouse.png',
                                        'shape': 'rect'}}
        self.object_number = 0
        self.static = True
        self.a_bord = []
        self.b_bord = []
    def draw(self):
        self.camera.view(self.scene)

        if self.DEVMODE:
            self.camera.devview(self.scene)

        self.camera.show(self.DEVMODE)

        for overlay in self.overlays:
            overlay.draw()

        pygame.display.update()

    def static_invert(self):
        """
        Выбор статического\динамического объекта
        """
        self.static = not self.static
        print('static mode = '+ str(self.static))
    """
    Дальше куча методов по выбору объекта и режима 
    """
    def mode_up(self):
        if self.mode_number < (len(self.modes) - 1):
            self.mode_number += 1
        else:
            self.mode_number = 0
        print(self.modes[self.mode_number])
    def mode_down(self):
        if self.mode_number > 0:
            self.mode_number -= 1
        else:
            self.mode_number = len(self.modes) - 1
        print(self.modes[self.mode_number])
    def obj_right(self):
        if self.object_number < (len(self.objects) - 1):
            self.object_number += 1
        else:
            self.object_number = 0
        if self.modes[self.mode_number] == 'object_placer':
            print(self.objects[self.object_number])
    def obj_left(self):
        if self.object_number > 0:
            self.object_number -= 1
        else:
            self.object_number = len(self.objects) - 1
        if self.modes[self.mode_number] == 'object_placer':
            print(self.objects[self.object_number])
    """
    Добавление выбранного объекта по позиции мыши
    """
    def object_appender(self, buttontype, screencoords = None):
        """
        Добавление выбранного объекта по позиции мыши
        """
        coords = self.camera.screen_coords_to_physical(screencoords)
        #coords[1] = -coords[1]
        if self.modes[self.mode_number] == 'object_placer':
            object_name = self.objects[self.object_number]
            char_dict = self.placeable_objects[object_name]
            if char_dict['shape'] == 'rect':
                if self.static == True:
                    self.scene.add_to_level('StaticRectangularObject', coords[0], coords[1],
                                            char_dict['width'],
                                            char_dict['height'],
                                            char_dict['sprite_adress'])
                    print('static rect object placed')
                else:
                    self.scene.add_to_level('DynamicRectangularObject', coords[0], coords[1],
                                            char_dict['width'],
                                            char_dict['height'],
                                            char_dict['sprite_adress'])
                    print('dynamic rect object placed')
            else:
                self.scene.add_to_level('StaticRectangularObject', coords[0], coords[1],
                                        char_dict['radius'],
                                        char_dict['sprite_adress'])
                print('dynamic circ object placed')
        elif self.modes[self.mode_number] == 'border_placer':
            if buttontype == 'leftbutton':
                self.a_bord = coords
                print('a point set')
            if buttontype == 'rightbutton':
                self.b_bord = coords
                print('b point set')
            if buttontype == 's':
                if not (self.b_bord == [] and self.a_bord == []):
                    self.scene.physical_space.add(pymunk.Segment(self.scene.physical_space.static_body,
                                                                   self.a_bord, self.b_bord, 1))
                print('border set')

    def save_to_file(self, filename = 'default_level'):
        """
        Сохранение уровня в файл
        """

        self.scene.save_level(filename)
        print('level saved as '+ str(filename))

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
            if pygame.mouse.get_pressed(3)[2]:
                self.object_appender('rightbutton', pygame.mouse.get_pos())
                #print('rtouch')
            if pygame.mouse.get_pressed(3)[0]:
                self.object_appender('leftbutton', pygame.mouse.get_pos())
                #print('ltouch')
            if event.type == pygame.MOUSEWHEEL:
                self.camera.distance -= event.y
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_r]:
                    self.camera.position = 0, 0
                    self.camera.distance = 14
                if pygame.key.get_pressed()[pygame.K_F3]:
                    self.DEVMODE = not self.DEVMODE
                if pygame.key.get_pressed()[pygame.K_UP]:
                    self.mode_up()
                if pygame.key.get_pressed()[pygame.K_DOWN]:
                    self.mode_down()
                if pygame.key.get_pressed()[pygame.K_RIGHT]:
                    self.obj_right()
                if pygame.key.get_pressed()[pygame.K_LEFT]:
                    self.obj_left()
                if pygame.key.get_pressed()[pygame.K_o]:
                    self.static_invert()
                if pygame.key.get_pressed()[pygame.K_c]:
                    self.save_to_file()
                if pygame.key.get_pressed()[pygame.K_s]:
                    self.object_appender('s')
    def atexit(self):
        """
        Действия при выходе из приложения
        :return: следущеее приложение, которое запустится сразу или None, если не предусмотрено следущее
        """
        self.scene.save_level('editor_exit')


if __name__ == '__main__':
    app = App(micro_apps=[LevelEditor(screen, clock)])
    app.run()
