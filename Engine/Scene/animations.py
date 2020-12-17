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
from warnings import warn

import pygame

from Engine.utils.exceptions import NotSupportedConfig
from Engine.utils.exceptions import YouAreTeapot
from ..utils.utils import load_yaml, load_json, load_image, pil_to_pygame


class State(Enum):
    """
    Класс сотояний игрока, названия говорят сами за себя
    """
    IDLE = 'idle'  # ничего не делает

    WALKING = 'walking'  # идёт

    RUNNING = 'running'  # бежит

    SITTING = 'sitting'  # сидит на кортах

    SQUATTING = 'squatting'  # двигается на кортах

    LYING = 'lying'  # лежит

    CRAWLING = 'crawling'  # ползёт лёжа

    SOARING = 'soaring'  # парит в воздухе

    JUMPING = 'jumping'  # прыжок

    FLYING = 'flying'  # летит(в свободном падении)

    LANDING = 'landing'  # приземление

    # TODO: удалить следущие поля и методы
    # непропускемые
    non_permeable = [JUMPING, LANDING]

    # Группа воздушная
    air_group = SOARING, JUMPING, FLYING, LANDING

    @classmethod
    def is_air_group(cls, state):
        return state in cls.air_group


class IncorrectConfig(Exception):
    """
    Исключение, вызывающиеся при неправильном конфиге анимации
    """

    def __init__(self, text):
        super(IncorrectConfig, self).__init__(text)
        self.txt = text


def crop_image(picture, crops, flip_x, flip_y) -> list[pygame.Surface]:
    """
    Кропает изображение
    :param picture: изображение
    :param crops: список координат для кропа
        кроп имеет структуру:
                (x1, y1, x2, y2), где
                (x1, y1) это координаты левой верхней вершины описанного прямоугольника,
                (x2, y2) это координаты правой нижней вершины описанного прямоугольника
    :param flip_x: нужно ли отразить по оси x
    :param flip_y: нужно ли отразить по оси y
    :return: список pygame.Surface с кропами изображения
    """
    return [pygame.transform.flip(pil_to_pygame(picture.crop(coord)), flip_x, flip_y).convert_alpha() for coord in crops]


class AnimationLoader:
    """
    Загрузчик анимаций
    Содержит много статических методов, которые загружают разные анимации
    TODO: дописать загрузчики

    :raises :
    """

    @staticmethod
    def load_periodic_animation(config, flip_x=False, flip_y=True,
                                adaptive_width=True, adaptive_height=False, name=''):
        """
        Конфигурация должна быть словарём со следущими ключами:

        'type': 'periodic' # вот тут строго
        'locking': true/false # определяет, является ли анимация блокирующей
        'file': путь до файла со спрайтами
        'period': период анимации
        'coords': список кропов картинки

        :param name: Название анимации
        :param config: файл с конфигом анимации
        :param flip_x: нужно ли отразить по оси x
        :param flip_y: нужно ли отразить по оси y
        :param adaptive_width: адаптивная ширина (подробнее в документации в классе анимации)
        :param adaptive_height: адаптивная высота (подробнее в документации в классе анимации)
        :return:
        """

        if config['type'] != 'periodic':
            raise IncorrectConfig('Не верный тип анимации, должен быть periodic, а передан {}'.format(config['type']))

        # Загружаем картинку со спрайтами
        source = load_image(config['file'])

        try:
            return PeriodicAnimation(
                crop_image(source, config['coords'], flip_x, flip_y),
                config['period'],
                adaptive_width=adaptive_width, adaptive_height=adaptive_height,
                locking=config['locking']
            )
        except KeyError as e:
            raise IncorrectConfig(f'Нет нужного параметра для загрузки анимации {name}: {e}')

    @staticmethod
    def load_semi_periodic_animation(config, flip_x=False, flip_y=True,
                                     adaptive_width=True, adaptive_height=False, name=''):
        """
        Конфигурация должна быть словарём со следущими ключами:

        'type': 'semi_periodic' # вот тут строго
        'locking': true/false # определяет, является ли анимация блокирующей
        'file': путь до файла со спрайтами
        'non_periodic_time': время непериодической части анимации
        'period': период периодической части анимации
        'non_periodic_coords': список кропов картинки для непериодической части

        :param name: Название анимации
        :param config: файл с конфигом анимации
        :param flip_x: нужно ли отразить по оси x
        :param flip_y: нужно ли отразить по оси y
        :param adaptive_width: адаптивная ширина (подробнее в документации в классе анимации)
        :param adaptive_height: адаптивная высота (подробнее в документации в классе анимации)
        :return:
        """

        if config['type'] != 'semi_periodic':
            raise IncorrectConfig(
                'Не верный тип анимации, должен быть semi_periodic, а передан {}'.format(config['type']))

        # Загружаем картинку со спрайтами
        source = load_image(config['file'])

        try:
            return SemiPeriodicAnimation(
                crop_image(source, config['non_periodic_coords'], flip_x, flip_y),
                crop_image(source, config['coords'], flip_x, flip_y),
                config['non_periodic_time'],
                config['period'],
                adaptive_width=adaptive_width,
                adaptive_height=adaptive_height,
                locking=config['locking']
            )
        except KeyError as e:
            raise IncorrectConfig(f'Нет нужного параметра для загрузки анимации {name}: {e}')

    @staticmethod
    def load_non_periodic_animation(config, flip_x=False, flip_y=True,
                                    adaptive_width=True, adaptive_height=False, name=''):
        """
        Конфигурация должна быть словарём со следущими ключами:

        'type': 'periodic' # вот тут строго
        'locking': true/false # определяет, является ли анимация блокирующей
        'file': путь до файла со спрайтами
        'time_length': время анимации
        'coords': список кропов картинки

        :param name: Название анимации
        :param config: файл с конфигом анимации
        :param flip_x: нужно ли отразить по оси x
        :param flip_y: нужно ли отразить по оси y
        :param adaptive_width: адаптивная ширина (подробнее в документации в классе анимации)
        :param adaptive_height: адаптивная высота (подробнее в документации в классе анимации)
        :return:
        """

        if config['type'] != 'non_periodic':
            raise IncorrectConfig(
                'Не верный тип анимации, должен быть non_periodic, а передан {}'.format(config['type']))

        # Загружаем картинку со спрайтами
        source = load_image(config['file'])

        try:
            return NonPeriodicAnimation(
                crop_image(source, config['coords'], flip_x, flip_y),
                config['time_length'],
                adaptive_width=adaptive_width,
                adaptive_height=adaptive_height,
                locking=config['locking']
            )
        except KeyError as e:
            raise IncorrectConfig(f'Нет нужного параметра для загрузки анимации {name}: {e}')


@dataclass
class PeriodicAnimation:
    """
    Класс периодической анимации
    Хранит в себе спрайты и содержит методы, для выдачи нужных в нужное время
    интервал времени между картинками одинаковый
    """

    def __init__(self, frames: list[pygame.Surface] = None, period=1.,
                 adaptive_width=True, adaptive_height=False, locking=False):
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
        :param locking: блокирует ли эта анимация выполнение других,
         у переодической анимации это очень не желательно выставлять в True
        """

        # Может ли блокировать
        self.locking = locking

        if type(self) == PeriodicAnimation and self.locking:
            warn('Не стоит делать периодическую анимацию блокирующей')

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

        # Конечно, сущность можно проецировать на несколько камер
        # Можно хранить несколько спрайтов для разных дистанций, но зачем
        # Если всегда на сущность будет смотреть лишь одна камера

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
    """
    Полупериодичская анимация
    Сначала проигрывается непериодическая часть (один раз), потом периодическая (сколько надо)
    TODO: Дописать класс в случае необходимости
    """

    def __init__(self, non_frames_periodic=None, frames=None, non_periodic_time=1, period=1,
                 adaptive_width=True, adaptive_height=False, locking=False):
        super(SemiPeriodicAnimation, self).__init__(frames, period, adaptive_width, adaptive_height, locking)
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
class NonPeriodicAnimation(PeriodicAnimation):
    """
    Класс периодической анимации
    Хранит в себе спрайты и содержит методы, для выдачи нужных в нужное время
    интервал времени между картинками одинаковый
    """

    def __init__(self, frames: list[pygame.Surface] = None, time_length=0.5, adaptive_width=True,
                 adaptive_height=False, locking=False):
        super(NonPeriodicAnimation, self).__init__(frames=frames,
                                                   period=time_length,
                                                   adaptive_width=adaptive_width,
                                                   adaptive_height=adaptive_height,
                                                   locking=locking)

        self.time_length = time_length
        self.finished = False

    def reset(self):
        """
        Сбрасывает счётчик времени анимации в ноль
        :return: None
        """
        self.animation_time = 0
        self.finished = False

    def step(self, dt):
        """
        Инкрементирует счётчик времени на dt
        :param dt: квант времени
        :return: None
        """
        self.animation_time += dt
        if self.animation_time > self.time_length:
            self.finished = True

    def __str__(self):
        """
        Псевдопреобразовние в строку
        :return: общее сотояние классая
        """
        return f'RunOnceAnimation: Time length = {self.time_length}, Frames = {str(self.frames)}'

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

        # Если анимация закончилась, то выдаём последний кадр
        return self.scaled_frames[min(int(self.animation_time // self.frame_time), len(self.frames) - 1)]


@dataclass
class EntityAnimations:
    """
    Класс содержащий все возможные анимации сущности
    """

    def __init__(self, player, current_animation='idle_right'):
        """
        иницаилизируется либо без параметров, либо с желаемой начальной анимацие
        но это не важно, т.к. состояние почти сразу пересчитается

        Дублирование атрибутов нажно, чтобы не пересчитывать направление каждый кадр,
        возможно в следубщих весиях будет убрано для уменьшения использования озу, но пока так удобнее
        :param current_animation: начальное состояние ангимации
        """
        # TODO: добавить  анимации удара и пинка, прописать их физику

        # Сущность, к которой привязана анимация
        self.player = player

        # название анимации, которая проигрывается сейчас
        self.__current_animation = current_animation

        self.idle_left = PeriodicAnimation()  # ничего неделание влево
        self.idle_right = PeriodicAnimation()  # ничего неделание вправо

        self.walking_left = PeriodicAnimation()  # ходьба влево
        self.walking_right = PeriodicAnimation()  # ходьба вправо

        self.running_left = PeriodicAnimation()  # бег влево
        self.running_right = PeriodicAnimation()  # бег вправо

        self.sitting_left = PeriodicAnimation()  # сидение на кортах влево
        self.sitting_right = PeriodicAnimation()  # сидение на кортах вправо

        self.squatting_left = PeriodicAnimation()  # движение на кортах влево
        self.squatting_right = PeriodicAnimation()  # движение на кортах вправо

        self.lying_left = PeriodicAnimation()  # лежание влево
        self.lying_right = PeriodicAnimation()  # лежание вправо

        # ползанье влево не будет реализовано
        self.crawling_left = PeriodicAnimation()  # ползание влево
        self.crawling_right = PeriodicAnimation()  # ползание вправо

        # Эту пару анимаций, возможно, удалим, т.к. полёт для персонажей не планируется
        self.soaring_left = PeriodicAnimation()  # парение в воздухе влево
        self.soaring_right = PeriodicAnimation()  # парение в воздухе вправо

        self.jumping_left = NonPeriodicAnimation()  # прыжок влево
        self.jumping_right = NonPeriodicAnimation()  # прыжок вправо

        self.flying_up_right = PeriodicAnimation()  # полёт вверх вправо
        self.flying_up_left = PeriodicAnimation()  # полёт вверх влево
        self.flying_down_right = PeriodicAnimation()  # полёт вниз вправо
        self.flying_down_left = PeriodicAnimation()  # полёт вниз влево

        self.landing_left = NonPeriodicAnimation()  # приземление влево
        self.landing_right = NonPeriodicAnimation()  # приземлениеф вправо

    def __contains__(self, animation):
        """
        Проверяет, прописана ли анимация animation для персонажа
        :param animation: анимация
        :return:
        """
        return animation in self.__dict__

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

        # Старая анимация
        old_animation = self.__dict__[self.__current_animation]

        # Если анимация блокирующая
        if old_animation.locking:
            # print('locking')
            # Если есть артибут finished
            if hasattr(old_animation, 'finished'):
                # Если завершена
                # print('finishable')
                if not old_animation.finished:
                    return
                # print('not finished')
            else:
                return

        try:
            # обновляем внутреннюю переменную состояния
            self.__current_animation = newvalue

            # перезапускаем проигрываемую сечас анимацию
            self.__dict__[self.__current_animation].reset()

            # # Для дебага, не стоит удалять
            # print(f'Changed animation state {self.__current_animation} -> {newvalue}')

        except KeyError as e:
            msg = f'Не верная конфигурация. У {self.player.__class__.__name__}' \
                  f' нет анимации {"_".join(newvalue.split("_")[:-1])}.' \
                  f' Проверьте конфигурации персонажа'
            raise IncorrectConfig(msg) from e

    def step(self, dt):
        """
        Эволюционируем анимацию во времени
        TODO: добавить обработку непериодических анимаций
        :param dt: квант времени
        :return: None
        """
        animation = self.__dict__[self.__current_animation]
        if isinstance(animation, NonPeriodicAnimation) and animation.finished:
            animation_name = self.__current_animation.split('_')[0]
            if animation_name == State.JUMPING.value:
                self.player.state = State.FLYING, 'animation_step'
            else:
                self.player.state = State.IDLE, 'animation_step'

        else:
            animation.step(dt)

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
        Файл конфигурации должен иметь следующую структуру:

        {
        'name_1': {/*params_1*/},
        'name_2': {/*params_2*/},
        ...
        'name_n': {/*params_n*/}
        }

        name_i это имя анимации, в случаи игрока это:
        'idle'  # ничего не делает
        'walking'  # идёт
        'running'  # бежит
        'sitting'  # сидит на кортах
        'squatting'  # двигается на кортах
        'lying'  # лежит
        'crawling'  # ползёт лёжа
        'soaring'  # парит в воздухе
        'jumping'  # прыжок
        'flying'  # летит(в свободном падении)

        params_i зависит от типа анимации:
        periodic - периодическая анимация (PeriodicAnimation)
        semi_periodic - полупериодическая анимация (SemiPeriodicAnimation)
        non_periodic - непериодическая анимация (NonPeriodicAnimation)

        Для каждого вида анимации свои параметры,
        их можно посмотреть в документации соответсвующего метода в классе AnimationLoader

        Для этого метода нужно name,type и direction, все остальные параметры уже относятся к кокретному типу анимации

        Пример файла с конфигом:

        'walking': {
            'type': 'periodic',
            'period': 1,
            'file': 'src/Levels/player.png',
            'coords': [
                [240, 13, 315, 153],
                [335, 13, 410, 153],
                [423, 13, 498, 153],
                [515, 12, 590, 152]
            ],
            'direction': 'right'
        },

        'flying_up': {
            'type': 'semi_periodic',
            'non_periodic_time': 1,
            'period': 0.75,
            'file': 'src/Levels/player.png',
            'coords': [
                [75, 173, 175, 313],
                [195, 173, 295, 313],
                [415, 173, 515, 313],
                [535, 173, 635, 313],
                [645, 173, 745, 313]
            ],
            'non_periodic_coords': [
                [75, 173, 175, 313],
                [195, 173, 295, 313],
                [415, 173, 515, 313],
                [535, 173, 635, 313],
                [645, 173, 745, 313]
            ],
            'direction': 'right'
        }
        :param file_with_names: путь до конфигурационного файла
        :return: None
        """

        # Словарь подбирает подходящий загрузчик по типу анимации
        loader = {
            'periodic': AnimationLoader.load_periodic_animation,
            'semi_periodic': AnimationLoader.load_semi_periodic_animation,
            'non_periodic': AnimationLoader.load_non_periodic_animation
        }

        # TODO: долбавить проверку корректности всего (тут надо задолбаться)

        # Считывание файлов с диска
        # Поддерживаются yaml и json
        if file_with_names.endswith('.yaml'):
            animations: dict = load_yaml(file_with_names)
        elif file_with_names.endswith('.json'):
            animations: dict = load_json(file_with_names)
        else:
            raise NotSupportedConfig('Поддерживаются только файлы json и yaml')

        # Итерируетмся по анимациям
        for animation_name, animation in animations.items():

            # Если анимации ориентированны влево или вправо
            if (direction := animation['direction'].lower()) in ('right', 'left'):
                if direction == 'right':
                    directions = ('right', 'left')
                else:
                    directions = ('left', 'right')

                try:
                    # Анимация в прямом направлении
                    self.__dict__[f'{animation_name}_{directions[0]}'] = loader[animation['type']](
                        animation,
                        flip_x=False,
                        name=animation_name
                    )
                    # Анимация в зеркальном направлении
                    self.__dict__[f'{animation_name}_{directions[1]}'] = loader[animation['type']](
                        animation,
                        flip_x=True,
                        name=animation_name
                    )
                except IncorrectConfig as e:
                    raise IncorrectConfig(f'Неправильный конфиг для {self.player.__class__.__name__}') from e
