"""
Отвечающий за симулицию
100% поменяется в будущих версиях
"""

import os

import numpy as np
import yaml
from pygame.draw import rect, circle
from pymunk import Body, Segment, Poly, Circle

from Engine.Scene.game_objects import *
from Engine.utils.physical_primitives import PhysicalRect
from src.persons import PersonRegistry
from ..EntityControllers import ControllerRegistry

GRAVITY = Vec2d(0, -9.81)


class Background:
    """
    Класс заднего фона
    по идее просто замыленная фотка
    """

    def __view__(self, camera):
        """
        Проекция заднего фона на камеру
        :param camera:
        :return:
        """
        ...


class SunnyField(Background):
    """
    Класс простого заднего фона
    Солнце + небо + земля
    Горизонт на линии y = 0
    """

    def __view__(self, camera):

        # Проверка, пересекает ли плоскость камеры горизонт
        # Если пересекает
        if camera.position[1] ** 2 - camera.window_height ** 2 / 4 < 0:
            # Прямоугольник неба
            sky_rect = np.array([
                0,
                (camera.window_height / 2 - camera.position[1]),
                camera.window_width,
                (camera.window_height / 2 + camera.position[1]),
            ]) * camera.scale_factor

            # Прямоугольник земли
            ground_rect = np.array([
                0,
                0,
                camera.window_width,
                (camera.window_height / 2 - camera.position[1]),
            ]) * camera.scale_factor

            # Рисование
            rect(camera.temp_surface, (135, 206, 250), sky_rect)
            rect(camera.temp_surface, (34, 139, 34), ground_rect)

        # Камера выше горизонта
        elif camera.camera_rect.y > 0:
            # Заливаем экран небом
            rect(camera.temp_surface, (135, 206, 250), camera.temp_surface.get_rect())

        # Камера ниже горизонта
        elif camera.camera_rect.y < 0:
            # Заливаем экран землёй
            rect(camera.temp_surface, (34, 139, 34), camera.temp_surface.get_rect())

        # Рисекм солнце
        pt = camera.projection_of_point(np.array([2, 5]))
        circle(camera.temp_surface, (255, 255, 0), pt, camera.projection_of_length(1))


class GameEvent:
    """
    Класс игровый событий, вызываемых по условию
    """

    def __init__(self, condition, action):
        """
        :param condition: условия срабатывания
        :param action: действие
        """
        self.contition = condition
        self.action = action

    def hadle(self):
        if self.contition():
            self.action()


class Scene:
    """
    Класс игровой сцены, он же симулиция
    На основе сцены будут делаться уровни
    TODO: придумать систему ИГРОВЫХ событий, вызывающихся, в зависимости от услових
    TODO: например, по времени, здоровью игрока, от рандома, от колва очков игрока
    TODO: придумать, как сохранять состояние уровня
    """

    def __init__(self, game_app, background=SunnyField(), border=PhysicalRect(-10, -5, 20, 10)):
        """
        :param game_app: приложение игры, нужно для управления сценой
        """
        self.game_app = game_app
        # Игровые события
        self.game_events: list[GameEvent] = []
        # Предметы на игровом поле, например летающие ножи, частицы и т.д.
        self.objects = []
        # Живые сущности, например враги
        self.entities = []
        # Задний фон
        self.bg = background

        # Сама физика
        # физическое пространство
        self.physical_space = pymunk.Space()
        self.physical_space.gravity = GRAVITY

        # Граница уровня
        self.border = border
        top = pymunk.Segment(self.physical_space.static_body, self.border.topleft, self.border.topright, 0)
        bottom = pymunk.Segment(self.physical_space.static_body, self.border.bottomright, self.border.bottomleft, 0)
        right = pymunk.Segment(self.physical_space.static_body, self.border.topright, self.border.bottomright, 0)
        left = pymunk.Segment(self.physical_space.static_body, self.border.bottomleft, self.border.topleft, 0)

        bottom.friction = 1  # трение на полу

        self.physical_space.add(top)
        self.physical_space.add(bottom)
        self.physical_space.add(right)
        self.physical_space.add(left)

    def __view__(self, camera):
        """
        Отрисовка
        :param camera: камера, на поверхности которой рисуем
        :return:
        """
        camera.view(self.bg)
        for sub in self.objects:
            camera.view(sub)
        for ent in self.entities:
            camera.view(ent)

    def __devview__(self, camera):
        """
        Отрисовка параметров для разработчиков
        :param camera: камера, на поверхности которой рисуем
        :return:
        """
        camera.devview(self.bg)
        for sub in self.objects:
            camera.devview(sub)
        for ent in self.entities:
            camera.devview(ent)

        # координатные оси
        camera.project_line(np.array([0, -100]), np.array([0, 100]), (0, 0, 255), 3)
        camera.project_line(np.array([-100, 0]), np.array([100, 0]), (255, 0, 0), 3)

        # Границы уровня
        camera.project_line(
            self.border.topleft,
            self.border.topright,
            (139, 69, 19),
            3
        )

        camera.project_line(
            self.border.topright,
            self.border.bottomright,
            (139, 69, 19),
            3
        )

        camera.project_line(
            self.border.bottomright,
            self.border.bottomleft,
            (139, 69, 19),
            3
        )

        camera.project_line(
            self.border.bottomleft,
            self.border.topleft,
            (139, 69, 19),
            3
        )

    def step(self, dt):
        """
        Эволюция системы во времени
        :param dt: квант времени
        :return:
        """
        for game_event in self.game_events:
            game_event.hadle()

        # Расчёт физики
        self.physical_space.step(dt)

        for sub in self.objects:
            sub.step(dt)
        for ent in self.entities:
            ent.step(dt)


class Level(Scene):
    """
    Класс игрового уровня
    TODO: добавить методы сохранения и считывания из файла

    """

    def __init__(self, game_app, background=SunnyField(), border=PhysicalRect(-10, -5, 20, 10)):
        super(Level, self).__init__(game_app, background, border)

        # Выносим игрока отдельно, чтобы был удобный доступ к нему
        # Возможно так придётся вынести и антогонистов
        # Инициализируется в отдельном методе init_player
        self.player = None

    def step(self, dt):
        super(Level, self).step(dt)

        self.player.step(dt)

        # Возвращаем игрока в границы уровня
        self.player.check_scene_border(self.border)

    def __view__(self, camera):
        super(Level, self).__view__(camera)
        camera.view(self.player)

    def __devview__(self, camera):
        super(Level, self).__devview__(camera)
        camera.devview(self.player)

    # Методы, отвечающие за сохранение уровня в файла

    def save_level(self, username="defaultName"):
        """
        Функция сохранения уровня в ямл файл
        На вход принимает имя сохранения, если оно есть
        Иначе файл сохраняется как defaultName_save.yml
        На данный момент сохраняет только основные х-тики объектов,
        но реализовать сохранение доп х-тик довольно просто
        """
        # Словарь для сохранения
        save_data_final = {}

        # сохранение подвижных объектов вместе со спрайтами
        save_data_dict = {}
        for counter, object_ in enumerate(self.objects):
            save_data_dict[counter] = object_.save_data()
        save_data_final['objects'] = save_data_dict

        # Сохранение сущностей
        save_data_dict = {}
        counter = 0
        for entity in self.entities:
            save_data_dict[counter] = entity.save_data()
            counter += 1
        save_data_final['entities'] = save_data_dict

        # Сохранение гг
        save_data_final['MainCharacter'] = self.player.save_data()

        # Функция роется в движке и сохраняет все неподвижные физические тела без спрайтов
        save_data_dict = {}
        counter = 0
        for i in self.physical_space.shapes:
            if i.body.body_type == Body.STATIC:

                if isinstance(i, Segment):
                    save_data_dict[counter] = {'type': 'Segment', 'position': i.body.position,
                                               'a': i.a, 'b': i.b, 'r': i.radius}
                    counter += 1

                if isinstance(i, Poly):
                    save_data_dict[counter] = {'type': 'Poly', 'position': i.body.position}
                    counter += 1

                if isinstance(i, Circle):
                    save_data_dict[counter] = {'type': 'Circle', 'position': i.body.position,
                                               'offset': i.offset, 'r': i.radius}
                    counter += 1

        save_data_final['invisible_shit'] = save_data_dict

        with open(os.path.join('src', 'Levels', 'Saved_Levels', username + '_save'), 'w') as write_file:
            yaml.dump(save_data_final, write_file)

    # Методы, отвечающие за загрузку уровня из файла

    def init_player(self, x=0, y=0):
        """
        Инициализирует игрока
        :param x: x координата левого нижнего угла описанного прямоугольника игрока
        :param y: y координата левого нижнего угла описанного прямоугольника игрока
        :return:
        """
        self.player = PersonRegistry['MainCharacter'](self.physical_space, x, y)

    def spawn_entity(self, configs):
        self.entities.append(
            PersonRegistry[configs['class']](
                self.physical_space,
                *configs['vector'],
                ControllerRegistry[configs['brain']]
            )
        )

    def load_invisible_objects(self, object_dict):
        for object_ in object_dict.values():
            if object_['type'] == 'Segment':
                segment = pymunk.Segment(self.physical_space.static_body,
                                         object_['a'], object_['b'], object_['r'])
                segment.friction = 1
                self.physical_space.add(segment)

    def load_object(self, type_, x, y, width=None, height=None, sprite_adress=None):
        """
        Методы для помещения объектов в уровень
        Немного быдлокод, но рабочий
        """

        if type_ == 'StaticRectangularObject':
            self.objects.append(StaticRectangularObject(width=width, height=height,
                                                        sprite_adress=sprite_adress, x=x, y=y,
                                                        physical_space=self.physical_space))
        elif type_ == 'DynamicRectangularObject':
            self.objects.append(DynamicRectangularObject(width=width, height=height,
                                                         sprite_adress=sprite_adress, x=x, y=y,
                                                         physical_space=self.physical_space))
        elif type_ == 'DynamicCircularObject':
            self.objects.append(DynamicCircularObject(radius=width,
                                                      sprite_adress=sprite_adress, x=x, y=y,
                                                      physical_space=self.physical_space))

    def load_level(self, username):
        """
        Функция загрузки уровня из файла
        На вход принимает название сейва
        Если названия нет, подгружает резервный сейв под именем DefaultName_save
        P.S. такого резервного сейва еще нет
        """

        with open(os.path.join('src', 'Levels', 'Saved_Levels', username + '_save')) as readfile:
            data = yaml.load(readfile, Loader=yaml.Loader)

        if data == {}:
            return

        # Загрузка невидимых объектов
        # TODO: Юра назови это нормально, добавить документацию
        self.load_invisible_objects(data['invisible_shit'])

        # Загрузка объектов
        for object_ in data['objects'].values():
            self.load_object(type_=object_['class'], x=object_['vector'][0], y=object_['vector'][1],
                             height=object_['height'], width=object_['width'],
                             sprite_adress=object_['sprite_adress'])

        # Инициализация игрока
        self.init_player(*data['MainCharacter']['vector'])

        # Загрузка сущностей
        for entity_config in data['entities'].values():
            self.spawn_entity(entity_config)

    def create_level(self, location, save_name='save'):
        """
        Функция инициализации уровня
        На вход принимает локацию и сейв
        если сейва нет - юзает дефолтный сейв
        """

        self.bg = location.bg
        self.border = location.border
        self.load_level(save_name)
        hl = pymunk.Segment(self.physical_space.static_body,
                            (self.border.x, 0),
                            (self.border.x + self.border.width, 0),
                            0)
        hl.friction = 1

        self.physical_space.add(hl)
