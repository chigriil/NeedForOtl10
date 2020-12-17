"""
Отвечающий за симулицию
100% поменяется в будущих версиях
"""

import os

import numpy as np
import pygame
import pymunk
import yaml
from pygame.draw import rect, circle
from pymunk import Vec2d

from Engine.Scene.game_objects import PhysicalGameObject, ObjectRegistry
from Engine.utils.physical_primitives import PhysicalRect
from settings import g
from .camera import Camera
from .entities import PersonRegistry
from ..EntityControllers import ControllerRegistry

GRAVITY = Vec2d(0, -g)


class Background:
    """
    Класс заднего фона
    по идее просто замыленная фотка
    """

    def __init__(self, scene=None):
        self.scene = scene

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


class Dorm(Background):
    def __init__(self, scene=None):
        super(Dorm, self).__init__(scene=scene)
        self.image = pygame.image.load(os.path.join('Resources', 'pictures', 'Backgrounds',
                                                    'back_six.png'))
        self.image = pygame.transform.flip(self.image, True, True)

    def __view__(self, camera):
        borders = self.scene.borders
        screen_rect = camera.projection_of_rect(borders)
        camera.temp_surface.blit(pygame.transform.scale(self.image, (screen_rect[2], screen_rect[3])), screen_rect)


class Basment(Background):
    def __init__(self, scene=None):
        super(Basment, self).__init__(scene=scene)
        self.image = pygame.image.load(os.path.join('Resources', 'pictures', 'Backgrounds',
                                                    'back_basment.png'))
        self.image = pygame.transform.flip(self.image, True, True)

    def __view__(self, camera):
        borders = self.scene.borders
        screen_rect = camera.projection_of_rect(borders)
        camera.temp_surface.blit(pygame.transform.scale(self.image, (screen_rect[2], screen_rect[3])), screen_rect)


class Corridor(Background):
    def __init__(self, scene=None):
        super(Corridor, self).__init__(scene=scene)
        self.image = pygame.image.load(os.path.join('Resources', 'pictures', 'Backgrounds',
                                                    'back_corridor.png'))
        self.image = pygame.transform.flip(self.image, True, True)

    def __view__(self, camera):
        borders = self.scene.borders
        screen_rect = camera.projection_of_rect(borders)
        camera.temp_surface.blit(pygame.transform.scale(self.image, (screen_rect[2], screen_rect[3])), screen_rect)


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
    """

    def __init__(self, game_app, background=SunnyField(), borders=None):
        """
        :param game_app: приложение игры, нужно для управления сценой
        """
        self.game_app = game_app
        # Игровые события
        self.game_events: list[GameEvent] = []
        # Предметы на игровом поле, например летающие ножи, частицы и т.д.
        self.objects: list[PhysicalGameObject] = []
        # Живые сущности, например враги
        self.entities = []
        # Задний фон
        self.bg = background
        self.bg.scene = self
        # Сама физика
        # физическое пространство
        self.physical_space = pymunk.Space()
        self.physical_space.gravity = GRAVITY

        # Граница уровня
        self.borders = borders
        # Другие невидимые сегменты, например горизонт
        self.invisible_segments = []
        if self.borders is not None:
            self.add_borders()

    def add_borders(self):
        top = pymunk.Segment(self.physical_space.static_body, self.borders.topleft, self.borders.topright, 0)
        bottom = pymunk.Segment(self.physical_space.static_body, self.borders.bottomright, self.borders.bottomleft, 0)
        right = pymunk.Segment(self.physical_space.static_body, self.borders.topright, self.borders.bottomright, 0)
        left = pymunk.Segment(self.physical_space.static_body, self.borders.bottomleft, self.borders.topleft, 0)

        bottom.friction = 1  # трение на полу

        self.physical_space.add(top)
        self.physical_space.add(bottom)
        self.physical_space.add(right)
        self.physical_space.add(left)

        for invisible_segment in self.invisible_segments:
            new_segment = pymunk.Segment(self.physical_space.static_body,
                                         invisible_segment['start'],
                                         invisible_segment['end'],
                                         invisible_segment['radius'])
            new_segment.friction = 1
            self.physical_space.add(new_segment)

    def __view__(self, camera: Camera):
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

    def __devview__(self, camera: Camera):
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
            self.borders.topleft,
            self.borders.topright,
            (139, 69, 19),
            3
        )

        camera.project_line(
            self.borders.topright,
            self.borders.bottomright,
            (139, 69, 19),
            3
        )

        camera.project_line(
            self.borders.bottomright,
            self.borders.bottomleft,
            (139, 69, 19),
            3
        )

        camera.project_line(
            self.borders.bottomleft,
            self.borders.topleft,
            (139, 69, 19),
            3
        )

        for x in range(int(self.borders.left), int(self.borders.right) + 1):
            pygame.draw.line(
                camera.temp_surface,
                (0, 0, 0),
                (camera.projection_of_point((x, 0)).x, 0),
                (camera.projection_of_point((x, 0)).x, camera.temp_surface.get_height()),
                2
            )

        for y in range(int(self.borders.bottom), int(self.borders.top) + 1):
            pygame.draw.line(
                camera.temp_surface,
                (0, 0, 0),
                (0, camera.projection_of_point((0, y)).y),
                (camera.temp_surface.get_width(), camera.projection_of_point((0, y)).y),
                2
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

        for number, obj in enumerate(self.objects):
            obj.step(dt)
            # Если у объекта не осталось времени жизни, то удаляем его
            if obj.lifetime <= 0:
                obj.kill()
                self.objects.pop(number)

        for ent in self.entities:
            ent.step(dt)


class Level(Scene):
    """
    Класс игрового уровня
    TODO: добавить методы сохранения и считывания из файла

    """

    def __init__(self, game_app, background=SunnyField(), borders=None):
        super(Level, self).__init__(game_app, background, borders)

        # Выносим игрока отдельно, чтобы был удобный доступ к нему
        # Возможно так придётся вынести и антогонистов
        # Инициализируется в отдельном методе init_player
        self.player = None

    def step(self, dt):
        super(Level, self).step(dt)

        self.player.step(dt)

        # Возвращаем игрока в границы уровня
        self.player.check_scene_border(self.borders)

        # Проверяем урон по персонажам от объектов
        for obj in self.objects:
            # если объект способен наносить урон
            if obj.damage is not None:
                # считаем, что бросивший не получает урон от этого объекта
                if self.damage_in_area(obj.body_rect, obj.damage, 'from_dynamic_object', object_=obj, skip=[obj.owner]):
                    obj.damaged_many()

    def __view__(self, camera):
        super(Level, self).__view__(camera)
        camera.view(self.player)

    def __devview__(self, camera):
        super(Level, self).__devview__(camera)
        camera.devview(self.player)

    @property
    def entities_and_player(self):
        return self.entities + [self.player]

    def damage_in_area(self, area: PhysicalRect, damage, type_, impulse=None, skip=None, **kwargs):
        """
        Наносит урон всем сущностям в заданых границах
        :param area: границы
        :param damage: урон
        :param type_: тип урона
        :param impulse: импуль при нанесении урона (кулаком)
        :param skip: список id сущностей, которые по какой-либо причине не получат урон
        :return: True, если был нанесён урон, False иначе
        """

        if skip is None:
            skip = []

        # флаг, отвечающий за то, что был нанесён урон
        damaged = False

        # Пинаем объекты
        if impulse is not None:
            for object_ in self.objects:
                if area.check_intersection(object_.body_rect):
                    object_.body.apply_impulse_at_local_point(impulse)

        # Наносим урон сущностям и игроку
        for entity in self.entities_and_player:

            # Пропускаем нужных сущностей
            if id(entity) in skip:
                continue

            # Если сущность в области нанесения урона
            if area.check_intersection(entity.body_rect):

                # подробнее читать в документации на этот метод
                if 'object_' in kwargs:
                    kwargs['object_'].damaged()

                # нанесение урона
                entity.get_damage(damage, type_)
                # флаг, был нанесён урон
                damaged = True

                # Передаём импульс, если он есть
                if impulse is not None:
                    entity.body.apply_impulse_at_local_point(impulse)

        return damaged

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
        save_data_final = dict()

        # Сохранение границ
        save_data_final['borders'] = self.borders.save_data()
        save_data_final['invisible_segments'] = self.invisible_segments

        # сохранение подвижных объектов вместе со спрайтами
        save_data_dict = {}
        for counter, object_ in enumerate(self.objects):
            save_data_dict[counter] = {
                'class': object_.__class__.__name__,
                'init': object_.save_data()
            }
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

        #Сохраннение фона
        if self.background.__class__.__name__ == Dorm:
            save_data_final['background'] = 'dorm'
        if self.background.__class__.__name__ == Basment:
            save_data_final['background'] = 'base'
        if self.background.__class__.__name__ == Corridor:
            save_data_final['background'] = 'corr'

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
        self.player = PersonRegistry['MainCharacter'](self, x, y)

    def load_entity(self, configs):
        self.entities.append(
            PersonRegistry[configs['class']](
                self,
                *configs['vector'],
                ControllerRegistry[configs['brain']]
            )
        )

    def spawn_entity(self, name, position, brain='Idle'):
        """
        Спавнит персонажа на уровне
        :param name: имя персонажа
        :param position: позиция
        :param brain: мозги
        :return:
        """
        self.entities.append(
            PersonRegistry[name](
                self,
                *position,
                ControllerRegistry[brain]
            )
        )

    def load_object(self, config):
        """
        Методы для помещения объектов в уровень
        Делает тоже почти тоже самое, что и spawn_object
        """
        self.objects.append(ObjectRegistry[config['class']](
            self,
            **config['init']
        ))

    def spawn_object(self, type_, position, velocity=Vec2d(0, 0), start_angle=0, angular_velocity=0):
        """
        Спавнит объект на игровой сцене
        :param type_: тип объекта
        :param position: позиция объекта
        :param velocity: начальная скорость
        :param start_angle: начальный угол
        :param angular_velocity: начальная угловая скорость
        :return:
        """

        # Класс объекта
        class_ = ObjectRegistry[type_]
        # Создаём объект
        obj = class_(
            self,
            *position,
            start_angle,
        )
        # Устанавливает скорость
        obj.body.velocity = velocity
        # Устанавливаем угловую скорость
        obj.body.angular_velocity = angular_velocity
        # Добавляем объект на сцену
        self.objects.append(obj)

    def load_level(self, username):
        """
        Функция загрузки уровня из файла
        На вход принимает название сейва
        Если названия нет, подгружает резервный сейв под именем DefaultName_save
        P.S. такого резервного сейва еще нет
        """
        lvl_path = os.path.join('src', 'Levels', 'Saved_Levels', username + '_save')
        if not os.path.exists(lvl_path):
            lvl_path = os.path.join('src', 'Levels', 'Saved_Levels', 'default_level_save')
        with open(lvl_path) as readfile:
            data = yaml.load(readfile, Loader=yaml.Loader)

        # Если нет данных выходим
        if data == {}:
            return

        # Загрузка границ
        self.borders = PhysicalRect(**data['borders']) if data['borders'] is not None else PhysicalRect(-10, -5, 20, 10)
        self.invisible_segments = data['invisible_segments']
        self.add_borders()
        self.background = data['background']
        if self.background == 'dorm':
            self.bg = Dorm(self)
        if self.background == 'corr':
            self.bg = Corridor(self)
        if self.background == 'base':
            self.bg = Basment(self)
        # Загрузка объектов
        for object_ in data['objects'].values():
            self.load_object(object_)

        # Инициализация игрока
        self.init_player(*data['MainCharacter']['vector'])

        # Загрузка сущностей
        for entity_config in data['entities'].values():
            self.load_entity(entity_config)
