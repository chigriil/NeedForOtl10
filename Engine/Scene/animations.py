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
from ..exceptions import YouAreTeapot
from ..utils import load_yaml, load_json, load_image, pil_to_pygame


class State(Enum):
    """
    Класс соcтояний игрока, названия говорят сами за себя
    """
    IDLE = 'idle'  # ничего не делает

    WALKING = 'walking'  # идёт

    RUNNING = 'running'  # бежит

    SITTING = 'sitting'  # сидит на кортах

    SQUATTING = 'squatting'  # двигается на кортах

    LYING = 'lying'  # лежит

    CRAWLING = 'crawling'  # ползёт лёжа

    SOARING = 'soaring'  # парит в воздухе

    FLYING = 'flying'  # летит(в свободном падении)

#
#class _Sprite(pygame.Surface):
#    def __init__(self, path):
#        img = pygame.image.load(path).convert_alpha()
#        super(_Sprite, self).__init__(img.get_size())
#        self.path = path


class AnimationLoader:
    """
    Загрузчик анимаций
    Содержит много статических методов, которые загружают разные анимации
    """

    # @staticmethod
    # def load_periodic_animation(source, coords, period, flip_x, flip_y=True):
    #     """
    #     Создаёт периодическую анимацию
    #     интервал времени между картинками одинаковый
    #     :param source: картика со спрайтами
    #     :param coords: координаты спрайтов
    #     :param period: период анимации
    #     :param flip_x: нужно ли отразить по оси x
    #     :param flip_y: нужно ли отразить по оси y
    #     :return: экземпляр класса периодической анимации
    #     """
    #     return PeriodicAnimation([
    #         pygame.transform.flip(pil_to_pygame(source.crop(coord)), flip_x, flip_y)
    #         for coord in coords], period)

    @staticmethod
    def load_periodic_animation(config, flip_x=False, flip_y=True):
        """
        TODO: добавть описание структуры конфига
        :param config: файл с конфигом анимации
        :param flip_x: нужно ли отразить по оси x
        :param flip_y: нужно ли отразить по оси y
        :return:
        """
        # source = source,
        #     coords=animation['coords'],
        #     period=animation['period'],
        #     flip_x=True
        source = load_image(config['file'])
        return PeriodicAnimation([
            pygame.transform.flip(pil_to_pygame(source.crop(coord)), flip_x, flip_y)
            for coord in config['coords']], config['period'])


@dataclass
class PeriodicAnimation:
    """
    Класс периодической анимации
    Хранит в себе спрайты и содержит методы, для выдачи нужных в нужное время
    интервал времени между картинками одинаковый
    """

    def __init__(self, frames: list[pygame.Surface] = None, period=1, adaptive_width=True, adaptive_height=False):
        """
        Конструктор без параметров создаеёт пустой класс,
        который выдаёт зелёный прямоугольник при запросе картинки

        adaptive_width и adaptive_height - флаги, отвечающие за адаптивную подстройку ширины и высоты картинок
        Если оба отключены, то в методе check_camera_distance картинки будут подстраивать под размер size
        Если включены оба, то ислючение YouAreTeapot, т.к. не по логике не будут маштабирповаться картинки
        :param adaptive_width: Пропорциональное изменение ширины картинки
        :param adaptive_height: Пропорциональное изменение высоты картинки
        :param frames: картинки анимации (экземпляры pygame.Surface)
        :param period: период анимации
        """

        # Флаги, отвечающие за адаптивную подстройку ширины и высоты картинок
        # Если оба отключены, то в методе check_camera_distance картинки будут подстраивать под размер size
        # Если включены оба, то ислючение
        # Пропорциональное изменение высоты картинки
        self.adaptive_height = adaptive_height
        # Пропорциональное изменение ширины картинки
        self.adaptive_width = adaptive_width

        if adaptive_width and adaptive_height:
            raise YouAreTeapot("Картинка должна маштабироваться")

        # Счётчик время проигрывания анимации
        self.animation_time = 0
        # Кадры анимации
        self.frames = frames
        # Отмаштабированные кадры анимации
        self.scaled_frames = frames
        # Последнее расстояние до камеры
        self.last_camera_distance = -1

        if self.frames is not None:
            # Время одного фрейма
            self.frame_time = period / len(self.frames)

            self.frame_width = self.frames[0].get_width()
            self.frame_height = self.frames[0].get_height()
        else:
            self.frame_time = 1
            self.frame_width = 1
            self.frame_height = 1

    def check_camera_distance(self, distance, size):
        if self.last_camera_distance == distance:
            return

        if self.adaptive_width:
            size = size[1] * self.frame_width // self.frame_height, size[1]

        elif self.adaptive_height:
            size = size[0], size[0] * self.frame_height // self.frame_width

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
        return f'PeriodicAnimation: Frametime = {self.frame_time}, Frames = {str(self.frames)}'

    def get(self, distance, size):
        """
        Возвращает картинку из анимации, соответсвующую времени
        если картинок нет, то возвращает зелёный прямоугольник
        :param distance: дистаниця до камеры
        :param size: размер окна, под который надо подгонять
        :return: картинку из анимации
        """

        # если нет, картинок возращам зелёный прямоугольник
        if self.frames is None:
            surf = pygame.Surface(size)
            surf.fill((0, 128, 0))
            return surf

        # Проверяем маштаб картинок
        self.check_camera_distance(distance, size)

        return self.scaled_frames[int(self.animation_time // self.frame_time) % len(self.frames)]


@dataclass
class SemiPeriodicAnimation(PeriodicAnimation):
    def __init__(self, non_frames_periodic=None, frames=None, non_periodic_time=1, period=1, adaptive_width=True,
                 adaptive_height=False):
        super(SemiPeriodicAnimation, self).__init__(frames, period, adaptive_width, adaptive_height)
        self.non_periodic_frames = non_frames_periodic
        self.non_periodic_time = non_periodic_time

        if self.non_periodic_frames is not None:
            # Время одного непериодического фрейма
            self.non_periodic_frame_time = period / len(self.non_periodic_frames)
        else:
            self.non_periodic_frame_time = 1

    def check_camera_distance(self, distance, size):
        super(SemiPeriodicAnimation, self).check_camera_distance(distance, size)


@dataclass
class OneRunAnimation(PeriodicAnimation):
    """
    TODO: вообзе хз как нормально писать блокирующий режим, и выход из анимации
    """

    def __str__(self):
        """
        Псевдопреобразовние в строку
        :return: общее сотояние классая
        """
        return f'OneRunAnimation: Frametime = {self.frame_time}, Frames = {str(self.frames)}'

    def get(self, distance, size):
        """
        Возвращает картинку из анимации, соответсвующую времени
        если картинок нет, то возвращает зелёный прямоугольник
        :param distance: дистаниця до камеры
        :param size: размер окна, под который надо подгонять
        :return: картинку из анимации или None, если картинки закончились
        """

        # если нет, картинок возращам зелёный прямоугольник
        if self.frames is None:
            surf = pygame.Surface(size)
            surf.fill((0, 128, 0))
            return surf

        # Проверяем маштаб картинок
        self.check_camera_distance(distance, size)

        if int(self.animation_time // self.frame_time) < len(self.frames):
            return self.scaled_frames[int(self.animation_time // self.frame_time)]

        return None


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

            # Тип анимации
            type_ = animation['type']

            # Загружаем картинку со спрайтами
            source = load_image(animation['file'])

            # Если анимации ориентированны влево или вправо
            if direction := animation['direction'].lower() in ('right', 'left'):
                if direction == 'right':
                    directions = ('right', 'left')
                else:
                    directions = ('left', 'right')

                if type_ == 'periodic':
                    # Анимация в прямом направлении
                    self.__dict__[f'{animation_name}_{directions[0]}'] = AnimationLoader.load_periodic_animation(
                        animation,
                        flip_x=True
                    )

                    # Анимация в зеркальном направлении
                    self.__dict__[f'{animation_name}_{directions[1]}'] = AnimationLoader.load_periodic_animation(
                        animation,
                        flip_x=False
                    )
