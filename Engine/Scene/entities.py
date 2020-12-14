"""
Модуль реализующий классы живых сущностей
Например игрока и врагов
"""
from math import degrees
from os import PathLike
from typing import Union

import pygame
import pymunk
from pymunk import Space

from Engine.utils.physical_primitives import PhysicalRect
from settings import critical_speed, critical_ground_collision, bounce_correction_speed
from .animations import EntityAnimations, State
from .game_objects import PhysicalGameObject
from ..EntityControllers import Idle


class Entity(PhysicalGameObject):
    """
    Базовый класс сущности (игрока и антогонистов)

    TODO: прикрутить атрибуты игрока, например здоровье, уклонение, и т.д.
    TODO: добавить объект кулаков и ног, чтобы можно было легко реализовать засчитывание урона
    TODO: очень желателдьно добавить подсчёт очков, нужно если вруг мы решим завести ии от OpenAI
    TODO: прикрутить анимацию удара
    TODO: прикрутить анимацию кидания
    TODO: придумать, как сохранять состояние игрока
    TODO: разделить толо игрока на само тело, ноги, руки, голову (нужно для удобной анимации ударов)
    """

    def __init__(self, physical_space: Space, x=0, y=0, width=0.7, height=1.8, mass=75, brain=Idle):
        """
        :param physical_space: физическое пространство
        :param x: x координата левого нижнего края сущности
        :param y: y координата левого нижнего края сущности
        :param height: высота сущности
        :param width: ширина сущности
        :param brain: мозги сущности, подробнее смотри в Engine/EntityControllers.py
        """

        super(Entity, self).__init__(x=x, y=y, width=width, height=height, sprite=None, sprite_adress=None,
                                     physical_space=physical_space,
                                     mass=mass, moment=float('inf'), elasticity=0,
                                     friction=0.6, type_=pymunk.Body.DYNAMIC)
        # float('inf'), чтобы исключить вращение

        # Описанные прямоугольники для разных состояний игрока
        # Нужны для пересчёта геометрии при смене состояния игрока
        # Названия говорят сами за себяф

        self.brain = brain(self)
        self.idle_rect = PhysicalRect(0, 0, width, height)
        self.walking_rect = PhysicalRect(0, 0, width, height)
        self.running_rect = PhysicalRect(0, 0, width, height * 134 / 140)

        self.sitting_rect = PhysicalRect(0, 0, width, height / 2)
        self.squatting_rect = PhysicalRect(0, 0, width, height / 2)

        self.lying_rect = PhysicalRect(0, 0, height, width)
        self.crawling_rect = PhysicalRect(0, 0, height, width)

        self.soaring_rect = PhysicalRect(0, 0, width, height)
        self.jumping_rect = PhysicalRect(0, 0, width, height)
        self.flying_rect = PhysicalRect(0, 0, width, height)
        self.landing_rect = PhysicalRect(0, 0, width, height)

        self.walk_speed = 1.5  # Скорость ходьбы сущности
        self.run_speed = 4  # Скорость бега сущности
        self.jump_speed = 4.5  # Скорость прыжка

        # Далее флаги, нужные для удобной обработки

        # Состояние сущности
        self.__state = State.IDLE
        # Горизонтальное направление взгляда (влево, вправо)
        self.horizontal_view_direction = 'right'
        # Вертикальное направление взгляда (вверх, вниз)
        self.vertical_view_direction = 'up'

        # Сами анимации
        self.animations = EntityAnimations(self)

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
        # print(f'Changing entity status {self.__state} -> {new_state}')

        # # Выводим в консоль вызывающую функцию (ДЛЯ ДЕБАГА)
        # print(f'State: {self.__state} -> {new_state}, Calling function = {calling_function}')

        # Устанавливаем новое состояние
        self.__state = new_state
        # Меняем геометрию
        self.set_new_shape(new_state.value)

    def set_new_shape(self, shape: str):
        """
        Меняет физическое тело
        Нужно для корретной обрабьотки физики при приседаниях и беге
        TODO: написать документацию
        :param shape: новая форма
        :return:
        """
        # Удаляем старое тело
        self.physical_space.remove(self.body)
        self.physical_space.remove(self.body_shape)

        # Новое тело
        self.body_shape = pymunk.Poly.create_box(self.body, self.__dict__[f'{shape}_rect'].size)
        self.body_shape.friction = 0.6
        self.body_shape.elasticity = 0
        self.body_rect = self.__dict__[f'{shape}_rect']
        self.body_rect.centre = self.body.position

        # считаем, что нижняя граница человека остаётся постоянной, типо он отталкивается ногами
        self.body.position += ((self.__dict__[f'{shape}_rect'].height - self.body_rect.height) / 2, 0)

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
        TODO: поправить проверку статуса FLYING, т. к. она слишком примитивная
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
        # TODO: ОПТИМИЗАЦИЯ
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

    def save_data(self):
        return {'class': self.__class__.__name__, 'width': self.width, 'height': self.height,
                'sprite_adress': self.sprite_adress, 'vector': self._position.__reduce__()[1], 'brain': self.brain.name}
