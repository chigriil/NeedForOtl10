"""
Отвечающий за симулицию
100% поменяется в будущих версиях
"""

import os
import numpy as np
import yaml
from pygame.draw import rect, circle

from Engine.Scene.game_objects import *
from Engine.Scene.physical_primitives import PhysicalRect
from src.persons import Player

# from Engine.Scene.animations import _Sprite

GRAVITY = np.array([0, -9.81])


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

    def init_player(self, x=0, y=0, width=0.9, height=1.8, sprite=None, sprite_adress=None, animations_config=None,
                    location=None):
        """
        Инициализирует игрока
        :param x:
        :param y:
        :param width:
        :param height:
        :param sprite:
        :param animations_config:
        :return:
        """
        self.location = location
        self.player = Player(self.physical_space, x, y, width, height, sprite_adress)
        self.player.load_animations(animations_config)
        self.entities.append(self.player)

    def step(self, dt):
        super(Level, self).step(dt)

        # Возвращаем игрока в границы уровня
        self.player.check_scene_border(self.border)

    def add_to_level(self, type_, x, y, width=None, height=None, sprite_adress=None):
        """
        Методы для помещения сущностей и объектов в уровень
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
        elif type_ == 'Player':
            self.init_player(width=width, height=height,
                             sprite_adress=sprite_adress, x=x, y=y, animations_config="src/Levels/test.yaml")

    def save_level(self, username="defaultName"):
        """
        Функция сохранения уровня в ямл файл
        На вход принимает имя сохранения, если оно есть
        Иначе файл сохраняется как defaultName_save.yml
        На данный момент сохраняет только основные х-тики объектов,
        но реализовать сохранение доп х-тик довольно просто
        """

        with open(os.path.join('src', 'Levels', 'Saved_Levels', username + '_save'), 'w') as write_file:
            # сохранение подвижных объектов вместе со спрайтами
            save_data_dict = {}
            for counter, object_ in enumerate(self.objects):
                save_data_dict[counter] = object_.save_data()
            save_data_final = {'objects': save_data_dict}
            yaml.dump(save_data_final, write_file)
            save_data_dict = {}
            for counter, entity in enumerate(self.entities):
                save_data_dict[counter] = entity.save_data()
            save_data_final = {'entities': save_data_dict}
            yaml.dump(save_data_final, write_file)
            # Функция роется в движке и сохраняет все неподвижные физические тела без спрайтов
            counter = 0
            save_data_dict = {}
            for i in self.physical_space.shapes:
                if i.body.__repr__() == 'Body(Body.STATIC)':
                    if (str(i.__class__) == "<class 'pymunk.shapes.Segment'>"):
                        save_data_dict[counter] = {'type': 'Segment', 'position': i.body.position, 'a': i._get_a(),
                                                   'b': i._get_b(), 'r':
                                                       i._get_radius()}
                        counter += 1
                    if (str(i.__class__) == "<class 'pymunk.shapes.Poly'>"):
                        save_data_dict[counter] = {'type': 'Poly', 'position': i.body.position}
                        counter += 1
                    if (str(i.__class__) == "<class 'pymunk.shapes.Circle'>"):
                        save_data_dict[counter] = {'type': 'Circle', 'offset': i._get_a(), 'position': i.body.position,
                                                   'r': i._get_radius()}
                        counter += 1
            save_data_final = {'invisible_shit': save_data_dict}
            yaml.dump(save_data_final, write_file)
            # print(i.body.position)
            # print(str(i.__class__) == "<class 'pymunk.shapes.Poly'>")
            # print(str(i.__class__) == "<class 'pymunk.shapes.Segment'>")
            # print(str(i.__class__) == "<class 'pymunk.shapes.Circle'>")

    def load_level(self, username):
        """
        Функция загрузки уровня из файла
        На вход принимает название сейва
        Если названия нет, подгружает резервный сейв под именем DefaultName_save
        P.S. такого резервного сейва еще нет
        """

        with open(os.path.join('src', 'Levels', 'Saved_Levels', username + '_save')) as readfile:
            data = yaml.load(readfile, Loader=yaml.Loader)
            for type_ in data.keys():
                if type_ == 'invisible_shit':
                    for number in data[type_].keys():
                        object_ = data[type_][number]
                        if object_['type'] == 'Segment':
                            self.physical_space.add(pymunk.Segment(self.physical_space.static_body,
                                                                   object_['a'], object_['b'], object_['r']))

                else:
                    for number in data[type_].keys():
                        object_ = data[type_][number]
                        self.add_to_level(type_=object_['class'], x=object_['vector'][0], y= object_['vector'][1],
                                          height=object_['height'], width=object_['width'],
                                          sprite_adress=object_['sprite_adress'])

    def create_level(self, location, save_name='hui'):
        """
        Функция инициализации уровня
        На вход принимает локацию и сейв
        если сейва нет - юзает дефолтный сейв
        """

        self.background = location.bg
        self.border = location.border
        self.load_level(save_name)
        hl = pymunk.Segment(self.physical_space.static_body,
                            (self.border.x, 0),
                            (self.border.x + self.border.width, 0),
                            0)
        hl.friction = 1

        self.physical_space.add(hl)
