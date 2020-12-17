"""
Модуль с классом камеры
TODO: если кому не лень сделайте юниттесты, типо мы дофига работаем
"""
import warnings
from enum import Enum
from math import pi, tan, atan

import pygame
from pygame import Rect
from pygame.draw import circle, line, polygon, rect
from pymunk import Vec2d

from Engine.Scene.entities import Entity
from Engine.utils.physical_primitives import PhysicalRect
from Engine.utils.pseudo_math import sigmoid, inverse_sigmoid
from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class CameraError(Exception):
    def __init__(self, text):
        super(CameraError, self).__init__(text)
        self.txt = text


class OperatorError(Exception):
    def __init__(self, text):
        super(OperatorError, self).__init__(text)
        self.txt = text


class OperatorWarning(Warning):
    def __init__(self, text):
        super(OperatorWarning, self).__init__(text)
        self.txt = text


class TargetingMethod(Enum):
    """
    Класс способов нацеливания на цель (да, да я тавтология)
    """

    # Мгновенное навередие
    INSTANT = 'instant'

    # Оконный
    # Задаётся допустимая область, в котолрой игрок передвигается без движения камеры
    # При вызоде игрока за грацу данной области, она сдвинется в направлении сдвига игрока
    WINDOW = 'window'

    # Плавное наведение
    # Камера будет плавно перемещаться к игроку
    SMOOTH = 'smooth'


class Camera:
    """
    Класс камеры, она смотрит на плоскость, с некоторого расстояния
    TODO: сделать функцию слежки за игроком (не чтобы игрок бы всегда в центре, небольшой гистерезис надо)
    TODO: сделать отключаемую проверку на границу уровня (функцию возврата камеры при пересечении грпницы)
    TODO: при надобности прикрутить несколько планоа камеры (передний, задний, несколько промежуточных)
    Это ^^^ скорее всего сохрёт 8173924787 фпс, поэтому вряд ли
    """

    def __init__(self, screen: pygame.Surface, x=0, y=0, h_fov=pi / 2, distance=15):
        # Экран, на который будет выводиться изображение
        self.screen = screen
        # Временная поверхность для рисования, потом блитится на экран
        self.temp_surface = pygame.Surface(screen.get_rect().size)

        # Далее физические характеристики камеры
        # Физические координаты центра камеры
        self.__position = Vec2d(x, y)
        # Горизонтальный угол обзора камеры
        self.h_fov = h_fov
        # Расстояние от камеры до поверхности экрана
        self.__distance = distance
        # Физическая ширина области вилимости камеры
        self.window_width = 2 * self.__distance * tan(self.h_fov / 2)
        # Физическая высота области вилимости камеры
        self.window_height = self.window_width * SCREEN_HEIGHT / SCREEN_WIDTH
        # Вертикальный угол обзора камеры
        self.v_fov = atan(self.window_height / self.__distance / 2)
        # Физическая область видимости камеры
        self.camera_rect = PhysicalRect(
            self.__position[0] - self.window_width / 2,
            self.__position[1] - self.window_height / 2,
            self.window_width,
            self.window_height
        )

        # Коэффициент, на который умножаются координаты, чтобы отрисовать объекты на экране на экране
        self.scale_factor = SCREEN_WIDTH / self.window_width
        self.dev_font = pygame.font.SysFont(pygame.font.get_fonts()[0], 50)

    def view(self, game_object):
        """
        Вызывает отрисовыку объекта на поверхности self.temp_surface
        :param game_object: сам объект, который отрисовывается
        :return:
        TODO: add devview
        """
        game_object.__view__(self)

    def devview(self, game_object):
        if hasattr(game_object, '__devview__'):
            game_object.__devview__(self)

    def show(self, devmode=False):
        """
        Вызывает отрисовку того, что было нарисованно на камере на экране
        :return: None
        """
        # Отражение по оси y, потомучто лень писать преобразования координат вообще везде
        # Предлагаю оставить это как есть
        # TODO: Если кто хочет сделайте нормально, т.к трансформации отнимают осень много фпс
        if devmode:
            self.DEVMODE_OVERLAY()

        # Отрисовка поверхности камеры на экране
        # Поворот нужен, чтобы не возиться с перевёрнутолй СК pygame по оси y
        self.screen.blit(pygame.transform.flip(self.temp_surface, False, True), (0, 0))
        # self.screen.blit(self.temp_surface,  (0, 0))
        # Очистка поверхности камеры
        self.temp_surface.fill((0, 0, 0))

    def DEVMODE_OVERLAY(self):
        """
        Девмод на камере
        :return:
        """
        temp_surface_rect = self.temp_surface.get_rect()
        circle(self.temp_surface, (255, 0, 0), temp_surface_rect.center, 10)
        line(self.temp_surface, (255, 0, 0), temp_surface_rect.midleft, temp_surface_rect.midright)
        line(self.temp_surface, (255, 0, 0), temp_surface_rect.midtop, temp_surface_rect.midbottom)
        # text_surf = self.dev_font.render("Привет", True, (255, 255, 0))
        # self.temp_surface.blit(text_surf, text_surf.get_rect().center)

    def return_to_borders(self, border: PhysicalRect):
        """
        Возращает камеру в границы
        :param border: границы
        :return: None
        """

        # По умолчанию считаем, что камеры смотрит крупнее, чем уровень
        x, y = border.centre

        # Если ширина области видимости камеры меньше ширины границ
        # Делаем, чтобы часть уровня за границей не была видна
        if self.camera_rect.width < border.width:
            x = self.camera_rect.centre.x
            x = max(x, border.left + self.camera_rect.width / 2)
            x = min(x, border.right - self.camera_rect.width / 2)

        # Если высота области видимости камеры меньше высоты границ
        # Делаем, чтобы часть уровня за границей не была видна
        if self.camera_rect.height < border.height:
            y = self.camera_rect.centre.y
            y = max(y, border.bottom + self.camera_rect.height / 2)
            y = min(y, border.top - self.camera_rect.height / 2)

        self.position = x, y

    def focus_point(self, target_point: Vec2d):
        """
        Фокусируется на точке
        :param target_point: целевая точка
        :return:
        """
        self.position = target_point

    def focus_rect(self, target_rect: PhysicalRect):
        """
        Фокусируется на центре target_rect
        :param target_rect: целевой прямоугольник
        :return:
        """
        self.position = target_rect.centre

    def screen_coords_to_physical(self, point):
        """
        Переводит экранные координаты в физические
        :param point: точка с экранными координатами
        :return: точка с физическими координатами
        """
        if not isinstance(point, Vec2d):
            point = Vec2d(point[0], point[1])

        return Vec2d(point.x, SCREEN_HEIGHT - point.y) / self.scale_factor - (
            self.window_width / 2 - self.__position[0],
            self.window_height / 2 - self.__position[1])

    def projection_of_point(self, point):
        """
        Считает проекцию точки на поверхность камеры
        :param point: точка, для которой считается проекция
        :return:
        """
        # Перевод в массив numpy
        if not isinstance(point, Vec2d):
            point = Vec2d(*point)

        return (point + (self.window_width / 2 - self.__position[0],
                         self.window_height / 2 - self.__position[1])) * self.scale_factor

    def projection_of_length(self, length):
        """
        Считает проекцию физической длины на экран
        :param length: физическая длина
        :return: длину проекции
        """
        return length * self.scale_factor

    def projection_of_lengths(self, lengths):
        """
        Считает проекции списка физических длин на экран
        :param lengths: физические длины
        :return: список длин проекций
        """
        return [self.projection_of_length(length) for length in lengths]

    def projection_of_rect(self, physical_rect: PhysicalRect) -> pygame.Rect:
        """
        Считает проекцию физического прямоугольника на поверхность камеры
        :param physical_rect: физический прямоугольник
        :return: экземпляр класса pygame.Rect, который есть проекция на экран
        """
        point = self.projection_of_point(physical_rect.bottomleft)
        return pygame.Rect(point, self.projection_of_lengths(physical_rect.size))

    def project_point(self, coords, radius, color=(0, 255, 0)):
        circle(self.temp_surface, color, self.projection_of_point(coords), radius)

    def project_line(self, start, end, color, width=1):
        """
        Рисует проекцию линии на поверхности камеры
        :param start: начальная физическая точка
        :param end: конечная физическая точка
        :param color: цвет
        :param width: ширина проекции
        :return:
        """
        line(self.temp_surface, color,
             self.projection_of_point(start),
             self.projection_of_point(end),
             width=width)

    def project_poly(self, vertices, color, width=0):
        """
        Проецирует физический прямоугольник на поверхность камеры
        :param vertices: вершины
        :param color: цвет
        :param width: толщина границы. Если = 0, то заполняется полностью
        :return:
        """
        vertices = [self.projection_of_point(vert) for vert in vertices]
        polygon(self.temp_surface, color, vertices, width=width)

    def project_rect(self, rect_: PhysicalRect, color, width=0):
        rect(self.temp_surface, color,
             Rect(
                 self.projection_of_point(rect_.bottomleft),
                 (self.projection_of_length(rect_.width), self.projection_of_length(rect_.height))
             ),
             int(self.projection_of_length(width)))

    def project_circle(self, centre, radius, color, width=0):
        """
        Проецирует круг на поверхность камеры
        :param centre: центр круга
        :param radius: радиус круга
        :param color: цвет круга
        :param width: толщина обводки. Если width = 0, то закрашивается весь круг
        """
        circle(self.temp_surface, color,
               self.projection_of_point(centre),
               self.projection_of_length(radius),
               int(width))

    def dev_rect(self, rect_: PhysicalRect, color, width=2):
        rect(self.temp_surface, color,
             Rect(
                 self.projection_of_point(rect_.bottomleft),
                 (self.projection_of_length(rect_.width), self.projection_of_length(rect_.height))
             ),
             width)

    @property
    def position(self):
        """
        Возращает физические координаты центра обзора
        :return: физические координаты центра камеры
        """
        return self.__position

    @position.setter
    def position(self, new_position):
        """
        Устанавливает новые физические координаты центра обзора
        :param new_position: новые физические координаты центра камеры
        :return: физические координаты центра камеры
        """
        # Изменение позиции
        self.__position = new_position
        # Пересчёт физической области видимости
        self.camera_rect = PhysicalRect(
            self.__position[0] - self.window_width / 2,
            self.__position[1] - self.window_height / 2,
            self.window_width,
            self.window_height
        )

    @property
    def distance(self):
        """
        Возращает физическое расстояние от камеры до сцены
        :return:
        """
        return self.__distance

    @distance.setter
    def distance(self, new_distance):
        """
        Возращает физическое расстояние от камеры до сцены
        :return:
        """
        if new_distance <= 0:
            # raise CameraError("Distance became negative")
            return

        # Расстояние от камеры до поверхности экрана
        self.__distance = new_distance
        # Физическая ширина области вилимости камеры
        self.window_width = 2 * self.__distance * tan(self.h_fov / 2)
        # Физическая высота области вилимости камеры
        self.window_height = self.window_width * SCREEN_HEIGHT / SCREEN_WIDTH
        # Вертикальный угол обзора камеры
        self.v_fov = atan(self.window_height / self.__distance / 2)
        # Физическая область видимости камеры
        self.camera_rect = PhysicalRect(
            self.__position[0] - self.window_width / 2,
            self.__position[1] - self.window_height / 2,
            self.window_width,
            self.window_height
        )
        # Коэффициент, на который умножаются координаты, чтобы отрисовать объекты на экране на экране
        self.scale_factor = SCREEN_WIDTH / self.window_width

        # Выводит в консоль основные параметры камеры
        # print('Width = {:.2f}\nHeight = {:.2f}\nDistance = {:.2f}\n'.format(self.window_width, self.window_height,
        #                                                                     self.__distance))

    def start(self):
        self.distance = self.__distance


class Operator:
    """
    Класс оператора камеры, наводит камеру на то, что нужно
    """

    def __init__(self, camera: Camera, method: TargetingMethod = TargetingMethod.SMOOTH):
        # Камера
        self.camera = camera
        # Цель, за которой будет следить оператор
        self.__target = None
        # Способ слежки
        self.targeting_method = method
        # Следит ли оператор сейчас
        self.aiming = False
        # Скорость камеры при плавном перемещении
        self.max_speed = 10
        # Особое время
        self.critical_time = 0.2
        # Растояние, на котором камера не будет больше приблежаться
        # Должно удовлетворять no_motion_distance < max_speed * critical_time
        # Тут для примера с коеффициентом 0.5
        self.no_motion_distance = self.max_speed * self.critical_time / 2
        # Некие сдвиги для smooth_func
        self.bias = 2
        self.scale = sigmoid(self.bias)
        self.alpha = self.inverse_smooth_func(
            self.no_motion_distance / (self.max_speed * self.critical_time)) / self.no_motion_distance

    @property
    def target(self):
        """
        Возвращает текущую цель
        :return:
        """
        return self.__target

    @target.setter
    def target(self, new_target):
        """
        Устанавливает новую цель
        :param new_target: новая цель
        :return:
        """
        self.__target = new_target

    def step(self, dt):
        """
        Размышления оператора от передвижении камеры
        :param dt: квант времени
        :return:
        """
        # Если нет цели, то выходим
        if self.__target is None or not self.aiming:
            return

        if self.targeting_method == TargetingMethod.INSTANT:
            self.instant_focus()
        elif self.targeting_method == TargetingMethod.WINDOW:
            self.window_focus()
        elif self.targeting_method == TargetingMethod.SMOOTH:
            self.smooth_focus(dt)

        else:
            warnings.warn(f'Нужно определить тип нацеливания {self.targeting_method} у оператора', OperatorWarning)

    def instant_focus(self):
        if isinstance(self.__target, Entity):
            self.camera.focus_rect(self.__target.body_rect)
        elif isinstance(self.__target, Vec2d):
            self.camera.focus_point(self.__target)
        elif isinstance(self.__target, PhysicalRect):
            self.camera.focus_rect(self.__target)

    def window_focus(self):
        # TODO: Дописать метод
        pass

    def smooth_focus(self, dt):
        if isinstance(self.__target, Entity):
            self.__smooth_focus(self.__target.body_rect.centre, dt)
        elif isinstance(self.__target, Vec2d):
            self.__smooth_focus(self.__target, dt)
        elif isinstance(self.__target, PhysicalRect):
            self.__smooth_focus(self.__target.centre, dt)

    def __smooth_focus(self, point, dt):
        # TODO: поколдовать с функцией, и учесть всякие точки перегиба
        direction = point - self.camera.position
        velocity = direction
        if (sm := self.smooth_func(self.alpha * direction.length)) != 0:
            velocity.scale_to_length(self.max_speed * sm)
        else:
            velocity = Vec2d(0, 0)
        self.camera.position += velocity * dt

    def smooth_func(self, x):
        return 1 - sigmoid(self.bias - x) / self.scale

    def inverse_smooth_func(self, x):

        return self.bias - inverse_sigmoid((1 - x) * self.scale)
