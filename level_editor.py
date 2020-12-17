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
import os
import sys

import numpy as np
import pygame
import pymunk

import Engine.utils.__dark_magic__ as dark_magic
from Engine.Scene.camera import Camera
from Engine.Scene.gamescene import Level
from Engine.apps import App, MicroApp
from Engine.gui.overlays import FPS
from Engine.utils.utils import load_yaml
from settings import *
from src.game import Game


def parse_objects():
    """
    ВОзвращает список доступных игровых объектов
    :return:
    """

    objects = []

    for game_object_config_file in os.listdir(game_objects_configs_path):

        if not game_object_config_file.endswith('.yaml'):
            continue

        config = load_yaml(os.path.join(game_objects_configs_path, game_object_config_file))

        objects.append(config['name'])

    return objects


def parse_persons():
    """
    Возвращает список персонажей
    :return:
    """

    persons = []

    for person_config_file in os.listdir(person_configs_path):

        if not person_config_file.endswith('.yaml') or person_config_file.startswith('_'):
            continue

        config = load_yaml(os.path.join(person_configs_path, person_config_file))

        persons.append(config['name'])

    return persons


class LevelEditor(MicroApp):
    """
    Собсна, редактор уровней
    """

    def __init__(self, screen, clock, load_file, saving_file):
        super(LevelEditor, self).__init__(screen, clock, lifetime=float('inf'))
        self.FPS = 0
        self.load_file = load_file
        self.saving_file = saving_file
        self.scene = Level(Game)
        self.scene.load_level(self.load_file)
        self.camera = Camera(self.screen, distance=16)
        self.camera.start()
        self.overlays = [FPS(self.screen, self.clock)]
        self.DEVMODE = DEVMODE
        self.modes = ['bg_select', 'border_placer', 'object_placer', 'entity_placer', 'camera_motion', 'load_from',
                      'save_to']
        self.mode_number = 0
        self.objects = parse_objects()
        self.persons = parse_persons()
        self.object_number = 0
        self.person = 'MainCharacter'
        self.static = True
        self.last_placed_is_object = True
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
        print('static mode = ' + str(self.static))

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

    def pers_right(self):
        if self.persons.index(self.person) + 1 < len(self.persons):
            self.person = self.persons[self.persons.index(self.person) + 1]
        else:
            self.person = self.persons[0]
        if self.modes[self.mode_number] == 'entity_placer':
            print(self.person)

    def pers_left(self):
        if self.persons.index(self.person) + 1 > 0:
            self.person = self.persons[self.persons.index(self.person) - 1]
        else:
            self.person = self.persons[len(self.persons) - 1]
        if self.modes[self.mode_number] == 'entity_placer':
            print(self.person)

    def mainCharacter_placed(self):
        for i in self.scene.entities:
            if i.save_data()['class'] == 'MainCharacter':
                return True
        return False

    """
    Добавление выбранного объекта по позиции мыши
    """

    def object_appender(self, buttontype, screencoords=None):
        """
        Добавление выбранного объекта по позиции мыши
        """
        # Координаты клика мыши, переведенные в физические
        coords = self.camera.screen_coords_to_physical(screencoords)
        if self.modes[self.mode_number] == 'object_placer':
            self.scene.spawn_object(self.objects[self.object_number], coords)
            print(f'The {self.objects[self.object_number]} is placed'
                  f' in the position ({round(coords[0], 2)}, {round(coords[1], 2)})')

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

        elif self.modes[self.mode_number] == 'entity_placer' and buttontype == 'leftbutton':
            print(self.person == 'MainCharacter')
            if self.person == 'MainCharacter' and not self.mainCharacter_placed():
                self.scene.init_player(coords[0], coords[1])

    def save_to_file(self, filename='default_level'):
        """
        Сохранение уровня в файл
        """

        self.scene.save_level(filename)
        print('level saved as ' + str(filename))

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
                # print('rtouch')
            if pygame.mouse.get_pressed(3)[0]:
                self.object_appender('leftbutton', pygame.mouse.get_pos())
                # print('ltouch')
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
                    self.pers_right()
                if pygame.key.get_pressed()[pygame.K_LEFT]:
                    self.obj_left()
                    self.pers_left()
                if pygame.key.get_pressed()[pygame.K_o]:
                    self.static_invert()
                if pygame.key.get_pressed()[pygame.K_c]:
                    self.save_to_file(filename=self.saving_file)
                if pygame.key.get_pressed()[pygame.K_s]:
                    self.object_appender('s')

    def atexit(self):
        """
        Действия при выходе из приложения
        :return: следущеее приложение, которое запустится сразу или None, если не предусмотрено следущее
        """
        self.scene.save_level(self.saving_file + 'editor_exit')


def main():
    dark_magic.init()
    pygame.mixer.pre_init()
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    print('enter where to load from')
    load_file = input()
    print('enter where to save')
    saving_file = input()
    if len(saving_file) == 0:
        saving_file = 'default_level'
    if len(load_file) == 0:
        load_file = 'basic'
    app = App(micro_apps=[LevelEditor(screen, clock, saving_file=saving_file, load_file=load_file)])
    app.run()


if __name__ == '__main__':
    if sys.hexversion < 0x30900f0:
        raise SystemError("Даня, я знаю это ты. Установи питон 3.9.0 или выше")
    main()
