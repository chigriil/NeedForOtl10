"""
Тут храняться классы игрока и антогонистов
TODO: Подобрать более подходлящитее имя файлу
"""
from math import copysign

import pygame

from Engine.Scene.animations import State
from Engine.Scene.entities import Entity


class Player(Entity):
    """
    Класс игрока
    """

    def keyboard_handler(self, pressed_keys: list[int]):
        """
        TODO: Вынести этот метод из класса игрока, лучше сделать класс типо конроллера, чтобы была база для ии
        TODO: разрешить менять игроку взгляд и направление вдоль x во время полёта
        :param pressed_keys: список нажатых клавиш
        :return:
        """
        new_state = self.state
        velocity = self.body.velocity

        # Если сущность имеет опору под ногами
        if self.can_lean_on_feet():
            # Ходьба
            if pressed_keys[pygame.K_a] ^ pressed_keys[pygame.K_d]:
                new_state = State.WALKING
                if pressed_keys[pygame.K_a]:
                    velocity[0] = -self.walk_speed
                elif pressed_keys[pygame.K_d]:
                    velocity[0] = self.walk_speed

                # Бег
                if pressed_keys[pygame.K_LSHIFT]:
                    velocity[0] = copysign(self.run_speed, velocity[0])
                    new_state = State.RUNNING

                # Прыжок
            if pressed_keys[pygame.K_SPACE]:
                velocity[1] = self.jump_speed
                new_state = State.JUMPING

        self.body.velocity = velocity
        self.state = new_state, 'keyboard handler'
