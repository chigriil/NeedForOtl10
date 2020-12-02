"""
Модуль реализующий классы живых сущностей
Например игрока и врагов
"""
from math import degrees
from os import PathLike
from typing import Union

import pygame
import pymunk
from pygame import Surface
from pymunk import Space

from settings import critical_speed
from .animations import EntityAnimations, State
from .game_objects import PhysicalGameObject
from .physical_primitives import PhysicalRect


class Entity(PhysicalGameObject):
    """
    Базовый класс сущности (игрока и антогонистов)

    TODO: прикрутить атрибуты игрока, например здоровье, уклонение, и т.д.
    TODO: добавить объект кулаков и ног, чтобы можно было легко реализовать засчитывание урона
    TODO: очень желателдьно добавить подсчёт очков, нужно если вруг мы решим завести ии от OpenAI
    TODO: придумать, как сериализовать игрока и как делать конфиг
    TODO: прикрутить анимацию удара
    TODO: прикрутить анимацию кидания
    TODO: придумать, как сохранять состояние игрока
    TODO: разделить толо игрока на само тело, ноги, руки, голову (нужно для удобной анимации ударов)
    TODO: сделать так, чтобы отображался спрайт по умолчанию если не анимации, а если его нет, то тогда зелёный квадрат
    """

    def __init__(self, physical_space: Space, x=0, y=0, width=0.7, height=1.8, sprite: Surface = None, sprite_adress = None, mass=75):
        """
        :param physical_space: физическое пространство
        :param x: x координата левого нижнего края сущности
        :param y: y координата левого нижнего края сущности
        :param height: высота сущности
        :param width: ширина сущности
        :param sprite: спрайт сущности
        """

        super(Entity, self).__init__(x=x, y=y, width=width, height=height, sprite=sprite, sprite_adress = sprite_adress,
                                     physical_space=physical_space,
                                     mass=mass, moment=float('inf'), elasticity=0,
                                     friction=0.6, type_=pymunk.Body.DYNAMIC)
        # float('inf'), чтобы исключить вращение

        self.walk_speed = 1.5  # Скорость ходьбы сущности
        self.run_speed = 4  # Скорость бега сущности
        self.jump_speed = 4.5  # Скорость прыжка

        # Конечно, сущность можно проецировать на несколько камер
        # Можно хранить несколько спрайтов для разных дистанций, но зачем
        # Если всегда на сущность будет смотреть лишь одна камера

        # Далее флаги, нужные для удобной обработки

        # Cостояние сущности
        self.state = State.IDLE
        # Горизонтальное направление взгляда (влево, вправо)
        self.horizontal_view_direction = 'right'
        # Вертикальное направление взгляда (вверх, вниз)
        self.vertical_view_direction = 'up'

        # Сами анимации
        self.animations = EntityAnimations()


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

        x = max(x, border.leftborder + self.width / 2)
        x = min(x, border.rightborder - self.width / 2)
        y = max(y, border.bottomborder + self.height / 2)
        y = min(y, border.topborder - self.height / 2)

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

    def check_status(self):
        """
        Проверяем статус сущности
        в частности проверяем на FLYING и IDLE
        TODO: поправить проверку статуса FLYING, т. к. она слишком примитивная
        :return:
        """
        if abs(self.body.velocity.y) < 1e-3 and self.state == State.FLYING:
            self.state = State.IDLE

        elif abs(self.body.velocity.y) > 1e-1:
            self.state = State.FLYING

        if self.body.velocity.length <= critical_speed:
            self.state = State.IDLE

    def step(self, dt):
        """
        Реализует эволюцию сущности во времени
        :param dt: квант времени
        :return:
        """
        # Обрабатываем приземление и падение
        # вероятность двойного прыжка есть, TODO: норсально обработать приземление

        # Проверяем статус сущности
        self.check_status()
        # Проверяем направление взгляда сущности
        self.check_directions()

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
