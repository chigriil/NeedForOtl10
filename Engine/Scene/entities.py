"""
Модуль реализующий классы живых сущностей
Например игрока и врагов
"""
from enum import Enum

import pymunk
from pygame import Surface
from pymunk import Space

from Engine.Scene.game_objects import PhysicalGameObject
from .physical_primitives import PhysicalRect


class State(Enum):
    """
    Класс сотояний игрока, названия говорят сами за себя
    """
    IDLE = 0  # ничего не делает
    WALKING = 1  # идёт
    RUNNING = 2  # бежит
    FLYING = 3  # летит(в свободном падении)


class Entity(PhysicalGameObject):
    """
    Базовый класс сущности
    """

    def __init__(self, physical_space: Space, x=0, y=0, width=0.7, height=1.8, sprite: Surface = None, mass=75):
        """
        :param physical_space: физическое пространство
        :param x: x координата левого нижнего края сущности
        :param y: y координата левого нижнего края сущности
        :param height: высота сущности
        :param width: ширина сущности
        :param sprite: спрайт сущности
        """
        super(Entity, self).__init__(x=x, y=y, width=width, height=height, sprite=sprite,
                                     physical_space=physical_space,
                                     mass=mass, moment=float('inf'), elasticity=0,
                                     friction=0.6, type_=pymunk.Body.DYNAMIC)
        # float('inf'), чтобы исключить вращение

        self.walk_speed = 1  # Скорость ходьбы сущности
        self.run_speed = 4  # Скорость бега сущности
        self.jump_speed = 3  # Скорость прыжка

        # Конечно, сущность можно проецировать на несколько камер
        # Можно хранить несколько спрайтов для разных дистанций, но зачем
        # Если всегда на сущность будет смотреть лишь одна камера

        # Далее флаги, нужные для удобной обработки
        self.flying = False  # Находится ли игрок в свободном падении

        # Cостояние игрока
        self.state = State.IDLE

    def check_scene_border(self, border: PhysicalRect):
        x, y = self.body.position

        x = max(x, border.leftborder + self.width / 2)
        x = min(x, border.rightborder - self.width / 2)
        y = max(y, border.bottomborder + self.height / 2)
        y = min(y, border.topborder - self.height / 2)

        self.body.position = x, y

    def step(self, dt):
        """
        Реализует эволюцию сущности во времени
        :param dt: квант времени
        :return:
        """
        # Обрабатываем приземление и падение
        # вероятность двойного прыжка есть, TODO: норсально обработать приземление
        if abs(self.body.velocity.y) < 1e-3:
            self.state = State.IDLE

        elif abs(self.body.velocity.y) > 1e-1:
            self.state = State.FLYING

        self.body_rect = PhysicalRect(*self.body.position - (self.width / 2, self.height / 2), self.width, self.height)

    @property
    def position(self):
        return self.body.position - (self.width / 2, self.height / 2)
