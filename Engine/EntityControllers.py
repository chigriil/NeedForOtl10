"""
Модуль с мозгами для сущностей
"""
from math import copysign

import pygame

from .Scene.animations import State

ControllerRegistry = {}


class EntityController:
    """
    Базовый класс контролера сущности
    Отвечает за принятия сущностью решения о том, что делать в каждый момент времени
    """

    def __init__(self, entity, name='default_contr_name'):
        """

        :param entity: сама сущность
        """
        self.entity = entity
        self.name = name

    def step(self, dt):
        """
        Мыслительный процесс
        :param dt: квант времени
        :return:
        """
        pass

    def __init_subclass__(cls, **kwargs):
        ControllerRegistry[cls.__name__] = cls


class Idle(EntityController):
    def __init__(self, entity, name='default_contr_name'):
        super(Idle, self).__init__(entity=entity, name=name)

    """
    Ничего не делающий контроллер
    """


class ManualController(EntityController):
    """
    Управление сущностья с клавиатуры
    TODO: разрешить менять игроку взгляд и направление вдоль x во время полёта
    """

    def step(self, dt):

        pressed_keys = pygame.key.get_pressed()
        new_state = self.entity.state
        velocity = list(self.entity.body.velocity)

        # Бросок
        if pressed_keys[pygame.K_q] and hasattr(self.entity, 'throw'):
            self.entity.throw()

        # Если сущность имеет опору под ногами
        if self.entity.can_lean_on_feet():
            # Ходьба
            if pressed_keys[pygame.K_a] ^ pressed_keys[pygame.K_d]:
                new_state = State.WALKING
                if pressed_keys[pygame.K_a]:
                    velocity[0] = -self.entity.walk_speed
                elif pressed_keys[pygame.K_d]:
                    velocity[0] = self.entity.walk_speed

                # Бег
                if pressed_keys[pygame.K_LSHIFT]:
                    velocity[0] = copysign(self.entity.run_speed, velocity[0])
                    new_state = State.RUNNING

            # Прыжок
            if pressed_keys[pygame.K_SPACE]:
                velocity[1] = self.entity.jump_speed
                # РЫвок, чтобы на следащем шаге проверки не было опоры под ногами
                self.entity.body.position += (0, 0.05)
                new_state = State.JUMPING

        self.entity.body.velocity = velocity
        self.entity.state = new_state, 'keyboard handler'
