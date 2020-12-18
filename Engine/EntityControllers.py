"""
Модуль с мозгами для сущностей
"""
from math import copysign

import pygame

from .Scene.animations import State
from .utils.utils import *

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
    TODO: разберись в разнице между name и config
    """

    def __init__(self, entity, config='config_wasd.yaml', name='default_contr_name'):
        super(ManualController, self).__init__(entity, name)

        self.config = config

        self.throw = 0
        self.hand_hit = 0
        self.walk_left = 0
        self.walk_right = 0
        self.run = 0
        self.jump = 0

        self.unload_config()

    def unload_config(self):
        """
        Принимает yaml файл со списком кнопок в следующем порядке:
        Бросок,
        Удар,
        Идти влево,
        Идти вправо,
        Бег,
        Прыжок
        :return: list
        """
        control_list = load_yaml('src/configs/controllers/' + str(self.config))

        self.throw = control_list[0]
        self.hand_hit = control_list[1]
        self.walk_left = control_list[2]
        self.walk_right = control_list[3]
        self.run = control_list[4]
        self.jump = control_list[5]

    def step(self, dt):

        pressed_keys = pygame.key.get_pressed()
        new_state = self.entity.state
        velocity = list(self.entity.body.velocity)

        # Бросок
        if pressed_keys[self.throw] and hasattr(self.entity, 'throw'):
            target = None
            distance = float('inf')
            # наводка на ближайщую сущность
            for entity in self.entity.scene.entities_and_player:
                if entity == self.entity:
                    continue

                if (distance_ := (self.entity.body.position - entity.body.position).length) < distance:
                    target = entity.body.position
                    distance = distance_

            self.entity.throw(target)

        if pressed_keys[self.hand_hit] and hasattr(self.entity, 'hand_hit'):
            self.entity.hand_hit()

        # Если сущность имеет опору под ногами
        if self.entity.can_lean_on_feet():
            # Ходьба
            if pressed_keys[self.walk_left] ^ pressed_keys[self.walk_right]:
                new_state = State.WALKING
                if pressed_keys[self.walk_left]:
                    velocity[0] = -self.entity.walk_speed
                elif pressed_keys[self.walk_right]:
                    velocity[0] = self.entity.walk_speed

                # Бег
                if pressed_keys[self.run]:
                    velocity[0] = copysign(self.entity.run_speed, velocity[0])
                    new_state = State.RUNNING

            # Прыжок
            if pressed_keys[self.jump]:
                velocity[1] = self.entity.jump_speed
                # РЫвок, чтобы на следащем шаге проверки не было опоры под ногами
                self.entity.body.position += (0, 0.05)
                new_state = State.JUMPING

        self.entity.body.velocity = velocity
        self.entity.state = new_state, 'keyboard handler'
