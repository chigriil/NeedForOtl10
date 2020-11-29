"""
Модуль со всевозможными анимациями
TODO: Продумать мтруктуру конфигурационных файлов
TODO: добавить другие виды анимации
TODO: добавить блокирующий режим (то есть, чтобы анимация гарантировнно доигрывалась до конца, если нужно)
"""
from dataclasses import dataclass
from enum import Enum
from os import PathLike
from typing import Union

import pygame

from ..exceptions import NotSupportedConfig
from ..utils import load_yaml, load_json, load_image, pil_to_pygame


class State(Enum):
    """
    Класс сотояний игрока, названия говорят сами за себя
    """
    IDLE = 'idle'  # ничего не делает

    WALKING = 'walking'  # идёт

    RUNNING = 'running'  # бежит

    FLYING = 'flying'  # летит(в свободном падении)


class AnimationLoader:
    """
    Загрузчик анимаций
    Содержит много статических методов, которые загружают разные анимации
    """

    @staticmethod
    def load_periodic_animation(source, coords, period, flip_x, flip_y=True):
        """
        Создаёт периодическую анимацию
        интервал времени между картинками одинаковый
        :param source: картика со спрайтами
        :param coords: координаты спрайтов
        :param period: период анимации
        :param flip_x: нужно ли отразить по оси x
        :param flip_y: нужно ли отразить по оси y
        :return: экземпляр класса периодической анимации
        """
        return PeriodicAnimation([
            pygame.transform.flip(pil_to_pygame(source.crop(coord)), flip_x, flip_y)
            for coord in coords], period)


@dataclass
class PeriodicAnimation:
    """
    Класс периодической анимации
    Хранит в себе спрайты и содержит методы, для выдачи нужных в нужное время
    интервал времени между картинками одинаковый
    """

    def __init__(self, frames=None, period=1):
        """
        Конструктор без параметров создаеёт пустой класс,
        который выдаёт зелёный прямоугольник при запросе картинки
        :param frames: картинки анимации (экземпляры pygame.Surface)
        :param period: период анимации
        """
        # Счётчик время проигрывания анимации
        self.animation_time = 0
        # Кадры анимации
        self.frames = frames
        # Отмаштабированные кадры анимации
        self.scaled_frames = frames
        # Последнее расстояние до камеры
        self.last_camera_distance = -1
        # Время одного фрейма
        self.frametime = period / len(self.frames) if frames is not None else 1

    def check_camera_distance(self, distance, size):
        if self.last_camera_distance == distance:
            return
        self.scaled_frames = [pygame.transform.scale(frame, size) for frame in self.frames]

    def reset(self):
        """
        Сбрасывает счётчик времени анимации в ноль
        :return: None
        """
        self.animation_time = 0

    def step(self, dt):
        """
        Инкрементирует счётчик времени на dt
        :param dt: квант времени
        :return: None
        """
        self.animation_time += dt

    def __str__(self):
        """
        Псевдопреобразовние в строку
        :return: общее сотояние классая
        """
        return f'PeriodicAnimation: Frametime = {self.frametime}, Frames = {str(self.frames)}'

    def get(self, distance, size):
        """
        Возвращает картинку из анимации, соответсвующую времени
        если картинок нет, то возвращает зелёный прямоугольник 100*100
        :return: картинку из анимации
        """

        # если нет, картинок возращам зелёный прямоугольник 100*100
        if self.frames is None:
            surf = pygame.Surface(size)
            surf.fill((0, 128, 0))
            return surf

        # Проверяем маштаб картинок
        self.check_camera_distance(distance, size)

        return self.scaled_frames[int(self.animation_time // self.frametime) % len(self.frames)]


@dataclass
class EntityAnimations:
    """
    Класс содержащий все возможные анимации сущности
    """

    def __init__(self, current_animation='idle_right'):
        """
        иницаилизируется либо без параметров, либо с желаемой начальной анимацие
        но это не важно, т.к. состояние почти сразу пересчитается
        :param current_animation:
        """
        # название анимации, которая проигрывается сейчас
        self.__current_animation = current_animation

        self.idle_left = PeriodicAnimation()  # ничего неделание влево
        self.idle_right = PeriodicAnimation()  # ничего неделание вправо
        self.walking_left = PeriodicAnimation()  # ходьба влево
        self.walking_right = PeriodicAnimation()  # ходьба вправо
        self.running_left = PeriodicAnimation()  # бег влево
        self.running_right = PeriodicAnimation()  # бег вправо
        self.flying_up_right = PeriodicAnimation()  # полёт вверх вправо
        self.flying_up_left = PeriodicAnimation()  # полёт вверх влево
        self.flying_down_right = PeriodicAnimation()  # полёт вниз вправо
        self.flying_down_left = PeriodicAnimation()  # полёт вниз влево

    @property
    def current_animation(self) -> str:
        """
        Возвращает название проигрываемой анимации
        :return: None
        """
        return self.__current_animation

    @current_animation.setter
    def current_animation(self, newvalue: str):
        """
        Устанавливает новое название проигрываемой анимации
        :param newvalue: новое название
        :return: None
        """
        # Если новое название = строму, то выходим из функции
        if newvalue == self.__current_animation:
            return

        # обновляем внутреннюю переменную состояния
        self.__current_animation = newvalue

        # перезапускаем проигрываемую сечас анимацию
        self.__dict__[self.__current_animation].reset()

    def step(self, dt):
        """
        Эволюционируем анимацию во времени
        :param dt: квант времени
        :return: None
        """
        self.__dict__[self.__current_animation].step(dt)

    def get(self, distance, size) -> pygame.Surface:
        """
        Возращает картинку из анимации в соответствии со временем
        :return: картинку
        """
        return self.__dict__[self.__current_animation].get(distance, size)

    def __str__(self):
        """
        Строковое псевдопредставление класса
        :return:
        """
        # TODO: make it without +=
        animations = self.idle_left, self.idle_right, self.walking_left, self.walking_right, self.running_left, self.running_right
        res = ''
        for animation in animations:
            res += str(animation)
            res += '\n'
        return res

    def load_animations(self, file_with_names: Union[str, bytes, PathLike[str], PathLike[bytes], int]):
        """
        Загружает анимацию с соответствии с конфигурационным файлом
        поодерживаются yaml и json
        :param file_with_names: конфигурационный файл
        :return: None
        """
        # TODO: долбавить проверку корректности всего

        # Считывание файлов с диска
        # Поддерживаются yaml и json
        if file_with_names.endswith('.yaml'):
            animations: dict = load_yaml(file_with_names)
        elif file_with_names.endswith('.json'):
            animations: dict = load_json(file_with_names)
        else:
            raise NotSupportedConfig('Поддерживаются только файлы json и yaml')

        # Итерируетмся по нозваниям анимаций
        for animation_name in animations:

            # Выбираем анимацию с названием animation_name
            animation: dict = animations[animation_name]

            # Загружаем картинку со спрайтами
            source = load_image(animation['filename'])

            # Если анимации ориентированны влево или вправо
            if direction := animation['direction'].lower() in ('right', 'left'):
                if direction == 'right':
                    directions = ('right', 'left')
                else:
                    directions = ('left', 'right')

                # Анимация в прямом направлении
                self.__dict__[f'{animation_name}_{directions[0]}'] = AnimationLoader.load_periodic_animation(
                    source=source,
                    coords=animation['coords'],
                    period=animation['animation_period'],
                    flip_x=True
                )

                # Анимация в зеркальном направлении
                self.__dict__[f'{animation_name}_{directions[1]}'] = AnimationLoader.load_periodic_animation(
                    source=source,
                    coords=animation['coords'],
                    period=animation['animation_period'],
                    flip_x=False
                )
