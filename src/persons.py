"""
Тут храняться классы игрока и антогонистов
TODO: Подобрать более подходлящитее имя файлу
"""
import pygame
from pygame import Surface

from Engine.Scene.entities import Entity, State


class Player(Entity):
    """
    Класс игрока
    TODO: прикрутить атрибуты игрока, например здоровье, уклонение, и т.д.
    TODO: добавить объект кулаков и ног, чтобы можно было легко реализовать засчитывание урона
    TODO: очень желателдьно добавить подсчёт очков, нужно если вруг мы решим завести ии от OpenAI
    TODO: придумать, как сериализовать игрока и как делать конфиг
    TODO: прикрутить анимацию удара
    TODO: прикрутить анимацию кидания
    TODO: придумать, как сохранять состояние игрока
    TODO: разделить толо игрока на само тело, ноги, руки, голову (нужно для удобной анимации ударов)
    """

    def __init__(self, physical_space, x=0, y=0, width=0.9, height=1.8, img: Surface = None):
        super(Player, self).__init__(physical_space, x, y, width, height, img)
        self.walk_speed = 1.5
        self.jump_speed = 4.5

    def keyboard_handler(self, pressed_keys: list[int]):
        """
        TODO: Вынести этот метод из класса игрока
        :param pressed_keys:
        :return:
        """
        velocity = self.body.velocity

        # Если игрок не в свободном падении
        if self.state != State.FLYING:

            # Ходьба
            if pressed_keys[pygame.K_a] ^ pressed_keys[pygame.K_d]:
                self.state = State.WALKING
                if pressed_keys[pygame.K_a]:
                    velocity[0] = -self.walk_speed
                elif pressed_keys[pygame.K_d]:
                    velocity[0] = self.walk_speed
            else:
                velocity[0] = 0

            # Бег
            if pressed_keys[pygame.K_LSHIFT]:
                velocity[0] *= self.run_speed / self.walk_speed

            # Прыжок
            if pressed_keys[pygame.K_SPACE]:
                self.state = State.FLYING
                velocity[1] = self.jump_speed

        self.body.velocity = velocity
