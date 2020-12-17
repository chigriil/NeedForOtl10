"""
Модуль реализующий классы живых сущностей
Например игрока и врагов
"""
from math import degrees, sin, cos, atan, sqrt
from os import PathLike
from random import choice
from typing import SupportsFloat, Union
from warnings import warn

import pygame
import pymunk
from pymunk import Vec2d

from Engine.EntityControllers import ManualController, Idle
from Engine.Scene.animations import EntityAnimations, State
from Engine.Scene.game_objects import ObjectRegistry, PhysicalGameObject
from Engine.utils.physical_primitives import PhysicalRect
from settings import critical_speed, critical_ground_collision, bounce_correction_speed, critical_reloading, g
from ..utils.utils import load_yaml

# Реестр всех персонажей
PersonRegistry = {}

default_person = load_yaml('src/configs/persons/_default_person.yaml')


class Entity(PhysicalGameObject):
    """
    Базовый класс сущности (игрока и антогонистов)

    TODO: прикрутить атрибуты игрока, например здоровье, уклонение, и т.д.
    TODO: добавить объект кулаков и ног, чтобы можно было легко реализовать засчитывание урона
    TODO: очень желателдьно добавить подсчёт очков, нужно если вруг мы решим завести ии от OpenAI
    TODO: прикрутить анимацию удара
    TODO: разделить толо игрока на само тело, ноги, руки, голову (нужно для удобной анимации ударов)
    """

    def __init__(self, scene, x=0, y=0, width=0.7, height=1.8, mass=75, brain=Idle, animations=None):
        """
        :param scene: игровая сцена
        :param x: x координата левого нижнего края сущности
        :param y: y координата левого нижнего края сущности
        :param height: высота сущности
        :param width: ширина сущности
        :param brain: мозги сущности, подробнее смотри в Engine/EntityControllers.py
        """

        super(Entity, self).__init__(x=x, y=y, width=width, height=height, sprite=None,
                                     scene=scene,
                                     mass=mass, moment=float('inf'), elasticity=0,
                                     friction=0.6, type_=pymunk.Body.DYNAMIC)
        # float('inf'), чтобы исключить вращение

        # Сцена сущности
        self.scene = scene
        # Мозг сущности
        self.brain = brain(self)

        # Описанные прямоугольники для разных состояний игрока
        # Нужны для пересчёта геометрии при смене состояния игрока
        # Названия говорят сами за себя
        # Прописывание всего этого рукими можно удалить, но оно нужно для наглядности
        rects: dict = default_person['rects']
        self.idle_rect = PhysicalRect(0, 0, rects['idle_rect'][0], rects['idle_rect'][1])
        self.walking_rect = PhysicalRect(0, 0, rects['walking_rect'][0], rects['walking_rect'][1])
        self.running_rect = PhysicalRect(0, 0, rects['running_rect'][0], rects['running_rect'][1])

        self.sitting_rect = PhysicalRect(0, 0, rects['sitting_rect'][0], rects['sitting_rect'][1])
        self.squatting_rect = PhysicalRect(0, 0, rects['squatting_rect'][0], rects['squatting_rect'][1])
        self.lying_rect = PhysicalRect(0, 0, rects['lying_rect'][0], rects['lying_rect'][1])
        self.crawling_rect = PhysicalRect(0, 0, rects['crawling_rect'][0], rects['crawling_rect'][1])

        self.soaring_rect = PhysicalRect(0, 0, rects['soaring_rect'][0], rects['soaring_rect'][1])
        self.jumping_rect = PhysicalRect(0, 0, rects['jumping_rect'][0], rects['jumping_rect'][1])
        self.flying_rect = PhysicalRect(0, 0, rects['flying_rect'][0], rects['flying_rect'][1])
        self.landing_rect = PhysicalRect(0, 0, rects['landing_rect'][0], rects['landing_rect'][1])

        # Не меняющиеся атрибуты
        # Свойства сущности
        properties: dict = default_person['properties']
        self.walk_speed = properties['walk_speed']  # Скорость ходьбы сущности
        self.run_speed = properties['run_speed']  # Скорость бега сущности
        self.jump_speed = properties['jump_speed']  # Скорость прыжка
        # Максимальное здоровье
        self.max_health = properties['max_health']
        # Вероятность уклонения
        self.dodge = properties['dodge']
        # Сопротивление урону
        self.resistance = properties['resistance']

        # Атрибуты, которые в данный момент
        self.health = self.max_health

        # Далее флаги, нужные для удобной обработки

        # Состояние сущности
        self.__state = State.IDLE
        # Горизонтальное направление взгляда (влево, вправо)
        self.horizontal_view_direction = 'right'
        # Вертикальное направление взгляда (вверх, вниз)
        self.vertical_view_direction = 'up'

        # Сами анимации
        self.animations = EntityAnimations(self)
        if animations is not None:
            self.load_animations(animations)

    @property
    def state(self):
        """
        :return: Текущее состояние игрока
        """
        return self.__state

    @state.setter
    def state(self, new_state):
        """
        Устанавливает новое состояние игрока
        :param new_state: новое состояние
        :return: None
        """

        # Если передан кортеж, то считаем, что второе значение это имя вызывающей функции
        calling_function = None
        if hasattr(new_state, '__getitem__'):
            new_state, calling_function = new_state

        # Если новое состояние равно старому, то выходим из функции
        if new_state == self.__state:
            return

        # # Выводим в консоль вызывающую функцию (ДЛЯ ДЕБАГА)
        # print(f'State: {self.__state} -> {new_state}, Calling function = {calling_function}')

        # Устанавливаем новое состояние
        self.__state = new_state
        # Меняем геометрию
        self.set_new_shape(new_state.value)

    def damage(self, damage):
        self.health -= damage / (1 + self.resistance)

    def set_new_shape(self, shape: str):
        """
        Меняет физическое тело
        Нужно для корретной обработки физики при приседаниях и беге
        :param shape: новая форма
        :return:
        """
        # Удаляем старое тело
        self.kill()

        # Новое тело
        self.body_shape = pymunk.Poly.create_box(self.body, self.__dict__[f'{shape}_rect'].size)
        self.body_shape.friction = 0.6
        self.body_shape.elasticity = 0

        old_bottom_left = self.body_rect.bottomleft
        self.body_rect = self.__dict__[f'{shape}_rect']

        # считаем, что нижняя граница человека остаётся постоянной, типо он отталкивается ногами
        self.body_rect.bottomleft = old_bottom_left

        self.body.position = self.body_rect.centre

        self.physical_space.add(self.body, self.body_shape)

    def load_animations(self, file_with_names: Union[str, bytes, PathLike[str], PathLike[bytes], int]):
        """
        Загружает анимации согласно конфигурационному файлу
        подробное описание структуры этого файла в readme (будет, а пока только пример)

        animations = {
        'idle': {
            'filename': 'src/Levels/player.png',
            'coords': [
                [80, 15, 155, 155],
                [160, 15, 235, 155]
            ],
            'animation_period': 1,
            'direction':'right'
        },

        'walking': {
            'filename': 'src/Levels/player.png',
            'coords': [
                [240, 12, 315, 154],
                [335, 12, 410, 154],
                [423, 12, 498, 154],
                [515, 12, 590, 154]
            ],
            'animation_period': 1,
            'direction': 'right'
            }
        }

        :param file_with_names: путь к конфигурационному файлу
        :return: None
        """
        self.animations.load_animations(file_with_names)

    def check_scene_border(self, border: PhysicalRect):
        """
        Возвращает сущности в заданые границы
        :param border: border
        :return: None
        """
        x, y = self.body.position

        x = max(x, border.left + self.width / 2)
        x = min(x, border.right - self.width / 2)
        y = max(y, border.bottom + self.height / 2)
        y = min(y, border.top - self.height / 2)

        self.body.position = x, y

    def update_animation_state(self):
        """
        Обновляет состояние анимации сущности
        :return: None
        """
        if self.state != State.FLYING:
            self.animations.current_animation = f'{self.state.value}_{self.horizontal_view_direction}'
        else:
            self.animations.current_animation = f'{self.state.value}_{self.vertical_view_direction}_{self.horizontal_view_direction}'

    def check_directions(self):
        """
        Проверяет направление взгляда, и меняет параметры
        vertical_view_direction и horizontal_view_direction если нужно
        :return: None
        """
        # Проверяем направление взгляда
        # т.к. вычисления с плавующей точкой не до конца точны, то ноль это небольшой диапозон
        # в данном случае интервал (-critical_speed, critical_speed)

        # Если вертикальная скорость больше "нуля", то смотрим вверх
        # Если меньше "нули", то смотрим вниз
        if self.body.velocity.y > critical_speed:
            self.vertical_view_direction = 'up'
        elif self.body.velocity.y < -critical_speed:
            self.vertical_view_direction = 'down'

        # Если горизонтальная скорость больше "нуля", то смотрим вправо
        # Если меньше "нули", то смотрим влево
        if self.body.velocity.x > critical_speed:
            self.horizontal_view_direction = 'right'
        elif self.body.velocity.x < -critical_speed:
            self.horizontal_view_direction = 'left'

    def is_foothold(self, shape):
        """
        Проверят, стоит ли сущность ногами на этой форме
        :param shape: там форма
        :return:
        """
        return self.body_shape.shapes_collide(shape).normal.y < -critical_ground_collision

    def can_lean_on_feet(self):
        """
        Проверяет, может ли сущность опереться ногами на что-нибудь
        :return:
        """
        return any(map(self.is_foothold, self.physical_space.shapes))

    def check_status(self):
        """
        Проверяем статус сущности
        в частности проверяем на FLYING и IDLE
        :return:
        """

        # новое состояние
        new_state = State.FLYING

        foothold = self.can_lean_on_feet()

        # Есть ли опора для ног
        if foothold:
            new_state = State.IDLE
            # начал приземление
            if self.state == State.FLYING:
                self.state = State.LANDING, 'check_status'
                return

        # Если персонаж прыгает
        elif self.state == State.JUMPING and not foothold:
            return

        # Фильтруем отскоки при приземлении
        if self.state != State.FLYING and new_state == State.FLYING and \
                abs(self.body.velocity.y) < bounce_correction_speed:
            new_state = new_state if new_state == State.LANDING else self.state

        # Если приземлён
        if foothold:
            if abs(self.body.velocity.x) > self.walk_speed / 2:
                new_state = State.WALKING
            if abs(self.body.velocity.x) > (self.walk_speed + self.run_speed) / 2:
                new_state = State.RUNNING

            # не летит и скорость = 0, значит бездействует
            if self.body.velocity.length < critical_speed:
                new_state = State.IDLE

        # Конец статуса приземления будет, если игрок начинает двигать или закончилась анимация
        if new_state == State.IDLE and self.state == State.LANDING:
            return

        self.state = new_state, 'check_status'

    def step(self, dt):
        """
        Реализует эволюцию сущности во времени
        :param dt: квант времени
        :return:
        """

        # сущность думает что делать дальше
        self.brain.step(dt)

        # Проверяем направление взгляда сущности
        self.check_directions()

        # Проверяем статус сущности
        self.check_status()

        # Обновляем статус анимации
        self.update_animation_state()

        # Пересчитываем описанный прямоугольник с учётом позиции сущности
        self.body_rect.centre = self.body.position

        # Шаг анимации
        self.animations.step(dt)

    def __view__(self, camera):
        """
        Рисует сущность на поверхности камеры
        :param camera: сама камера
        :return:
        """
        # Проекция описанного прямоугольника на камеру
        rect_for_camera: pygame.Rect = camera.projection_of_rect(self.boundingbox2)

        # Если не пересекается с экраном, то не рисуем
        if not rect_for_camera.colliderect(camera.screen.get_rect()):
            return

        self.scaled_sprite = self.animations.get(camera.distance, camera.projection_of_rect(self.body_rect).size)
        # Рисуем спрайт сущности
        # Поворачиваем
        prepared_sprite = pygame.transform.rotate(self.scaled_sprite, -degrees(self.body.angle))
        # Рисуем
        camera.temp_surface.blit(prepared_sprite, prepared_sprite.get_rect(center=rect_for_camera.center).topleft)


class BaseCharacter(Entity):
    """
    Базовый класс игрового персонажа
    На основе него делаются остальные классы
    """
    configs = default_person

    def __init__(self, scene, x=0, y=0, brain=ManualController):
        super(BaseCharacter, self).__init__(scene, x, y, brain=brain, **self.configs['init'])

        # Имя персонажа
        self.name = self.__class__.__name__
        # Описание персонажа
        self.description = None

        # Боёвка
        hits: dict = default_person['hits']
        # Удары рукой
        self.arming = hits['arming']
        # Бросания
        self.throwing = hits['throwing']

        # Список названий ударов рукой
        self.arming_types = list(self.arming)
        # Список названия бросков
        self.throwing_types = list(self.throwing)

        # Обновляем свойства, согласно конфигу
        if 'properties' in self.configs:
            self.__dict__ |= self.configs['properties']

        # Обновляем удары, согласно конфигу
        if 'hits' in self.configs:
            self.__dict__ |= self.configs['hit']

        # Обновляем описанные прямоугольники для разных состояний, согласно конфигу
        if 'rects' in self.configs:
            for name_, (width_, height_) in self.configs['rects'].items():
                self.__dict__[name_] = PhysicalRect(0, 0, width_, height_)

        # Атрибуты, которые в данный момент
        self.__arming_reload = 0
        self.__throwing_reload = 0

    def __init_subclass__(cls, **kwargs):
        PersonRegistry[cls.__name__] = cls

    @property
    def arming_reload(self):
        return self.__arming_reload

    @arming_reload.setter
    def arming_reload(self, value):
        self.__arming_reload = max(value, 0)

    @property
    def throwing_reload(self):
        return self.__throwing_reload

    @throwing_reload.setter
    def throwing_reload(self, value):
        self.__throwing_reload = max(value, 0)

    def step(self, dt):
        super(BaseCharacter, self).step(dt)
        # Перезарядка спссобностей
        self.arming_reload -= dt
        self.throwing_reload -= dt

    def set_attack_animation(self, method):
        """
        Устанавливает анимацию удара, проверяю прописана ли она в конфиге
        :param method:
        :return:
        """
        new_animation_name = f'{method["animation"]}_{self.horizontal_view_direction}'
        if new_animation_name in self.animations:
            self.animations.current_animation = new_animation_name
        else:
            msg = f'У персонажа {self.__class__.__name__}' \
                  f' нет анимации {method["animation"]} {"_".join(new_animation_name.split("_")[:-1])}.' \
                  f' Проверьте конфигурации персонажа'
            warn(msg)

    def _hit_box_to_physical_rect(self, box):
        physical_box = PhysicalRect(*box.values())
        physical_box.bottomleft += self.body_rect.bottomleft
        return physical_box

    def hand_hit(self):
        """
        Удар
        :return:
        """
        if self.arming_reload > critical_reloading:
            return
        print('hit')

        # Выбираем тип удара
        arming_method = self.arming[choice(self.arming_types)]

        # Устанавливаем анимацию удара, проверяю прописана ли она в конфиге
        self.set_attack_animation(arming_method)

        # Засчитываем урон
        self.scene.damage_in_area(self._hit_box_to_physical_rect(arming_method['box']), arming_method['damage'])

        # Устанавливаем время новое перезараядки
        self.arming_reload = arming_method['reload_time']

    def _throw(self, throw_method: dict, position: Vec2d, velocity: Vec2d, angle: SupportsFloat):
        """
        Бросание объекта
        :param throw_method: способ броска
        :param position: позиция броска, т. е. в которой спаниться объект
        :param velocity: скорость броска
        :param angle: угол броска
        :return: None
        """
        # Класс объекта, который кадаёт персонаж
        class_ = ObjectRegistry[throw_method['item']]
        # Создаём объект, который кинул персонаж
        obj = class_(
            self.scene,
            *position,
            angle,
        )
        # Устанавливает скорость
        obj.body.velocity = velocity
        # Устанавливаем угловую скорость
        obj.body.angular_velocity = throw_method['angular_speed']
        # Добавляем объект на сцену
        self.scene.objects.append(obj)

    def _throw_aiming_at_target(self, target: Vec2d, position: Vec2d, throw_method: dict) -> float:
        """
        Возращает угол, под которым надо просить тело, чтобы попасть в цель
        TODO: пофиксить это, т. к. наводка не верна. Скорее всего беды с формулами
        :param target: цель
        :param position: позиция, из которой происходит бросок
        :param throw_method: способ бросания
        :return: угол, по которым нужно бросать
        """
        dx, dy = target - position
        # Если направление взгляда совпадает с целью
        # TODO: может быть лучше менять взгляд во время кидания, а не кидать в никуда?
        if dx > 0 and self.horizontal_view_direction == 'right' or \
                dx < 0 and self.horizontal_view_direction == 'left':
            # Нужно, чтобы angle ∈ [-pi/2, pi/2]
            dx = abs(dx)
            # Скорость броска
            v = throw_method['throw_speed']
            # Физика 9 класса
            # Считаем тангенс угла
            # Для этого дискрименант делёный на V^4*dx^2
            d = 1 - 2 * g * dy / v / v - g * g * dx * dx * dx * dx / v / v / v / v

            # Кидаем на максимально возможную дистанцию
            tga = v * v / g / dx

            # print(d)

            # При положительном дискрименанте можно папасть, поэтому считаем угол
            if d >= 0:
                tga *= 1 - sqrt(d)

            return atan(tga)

        return throw_method['throw_angle']

    def throw(self, target=None):
        """
        Кидание
        :param target: цель,
        Если None, то угол броска берётся из конфига
        Если число, то угол броска = target
        Если вектор, то угол считается, так чтобы попасть в цель с координатами target по минимальной троектории или
        если не дотягивается, то кидаёт максимально близко к цели
        :return: None
        """
        # Если не перезарядилась перезарядка, то не кидаем новый
        if self.throwing_reload > critical_reloading:
            return

        # Выбираем способ броска
        throw_method = self.throwing[choice(self.throwing_types)]

        # Устанавливаем анимацию кадания, проверяю прописана ли она в конфиге
        self.set_attack_animation(throw_method)

        angle = throw_method['throw_angle']

        # Пересчитываем координаты с учётом направления взгляда
        if self.horizontal_view_direction == 'right':
            position = self.position + throw_method['position']
        else:
            position = self.position + Vec2d(
                self.width - throw_method['position'][0],
                throw_method['position'][1]
            )

        if target is not None:
            if isinstance(target, SupportsFloat):
                angle = target
            elif isinstance(target, Vec2d):
                angle = self._throw_aiming_at_target(target, position, throw_method)

        # Пересчитываем скорость с учётом направления взгляда
        if self.horizontal_view_direction == 'right':
            velocity = self.body.velocity + Vec2d(
                throw_method['throw_speed'] * cos(angle),
                throw_method['throw_speed'] * sin(angle)
            )
        else:
            velocity = self.body.velocity + Vec2d(
                -throw_method['throw_speed'] * cos(angle),
                throw_method['throw_speed'] * sin(angle)
            )

        # Кидание
        self._throw(throw_method, position, velocity, angle)

        # Устанавливаем время новое перезараядки
        self.throwing_reload = throw_method['reload_time']

    def save_data(self):
        return {'class': self.__class__.__name__, 'vector': list(self.position), 'brain': self.brain.__class__.__name__}
