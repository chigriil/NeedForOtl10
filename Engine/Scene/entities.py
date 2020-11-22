"""
Модуль реализующий классы живых сущностей
Например игрока и врагов
"""
from enum import Enum

import pygame
import pymunk
from pygame import Surface
from pymunk import Space

from Engine.Scene.game_objects import GameObject
from .physical_primitives import PhysicalRect


class State(Enum):
    """
    Класс сотояний игрока, названия говорят сами за себя
    """
    IDLE = 0
    WALKING = 1
    RUNNING = 2
    FLYING = 3


class Entity(GameObject):
    """
    Базовый класс сущности
    """

    def __init__(self, physical_space: Space, x=0, y=0, width=0.7, height=1.8, img: Surface = None):
        """
        :param physical_space: физическое пространство
        :param x: x координата левого нижнего края сущности
        :param y: y координата левого нижнего края сущности
        :param height: высота сущности
        :param width: ширина сущности
        :param img: спрайт сущности
        """
        # Начальные координаты левого нижнего края сущности
        # Нужны для реализиции некого костыля
        super(Entity, self).__init__(x, y, width, height, sprite=img)
        self.height = height  # Высота сущности
        self.width = width  # Ширина сущности
        # Хитбокс тела, на него нятигивается спрайт тела
        self.body_rect = PhysicalRect(*self._position, self.width, self.height)
        # Оригинальтная картинка спрайта
        self.base_image = pygame.transform.flip(img, False, True)

        self.walk_speed = 1  # Скорость ходьбы сущности
        self.run_speed = 4  # Скорость бега сущности
        self.jump_speed = 3  # Скорость прыжка

        # Преобразованное изображения спрайта
        # Имеет размер, как проекция сущности на поверхность камеры
        self.scaled_image = self.base_image  # Нужно для оптимизации
        self.last_camera_distance = -1  # Дистанция от камеры да сцены

        # Конечно, сущность можно проецировать на несколько камер
        # Можно хранить несколько спрайтов для разных дистанций, но зачем
        # Если всегда на сущность будет смотреть лишь одна камера

        # Далее флаги, нужные для удобной обработки
        self.flying = False

        # Cостояние игрока
        self.state = State.IDLE

        # Физика

        # Физическое пространство
        self.physical_space = physical_space

        # Масса сущности
        self.mass = 75

        # Цыганская магия
        # moment_of_inertia = pymunk.moment_for_box(self.mass, self.body_rect.size)
        moment_of_inertia = float("inf")  # убираем вращение игрока
        self.body = pymunk.Body(self.mass, moment_of_inertia, pymunk.Body.DYNAMIC)
        self.body.position = self.body_rect.centre
        self.body_shape = pymunk.Poly.create_box(self.body, self.body_rect.size)
        self.body_shape.elasticity = 0
        self.body_shape.friction = 0.6
        self.physical_space.add(self.body, self.body_shape)

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
        if abs(self.body.velocity.y) < 1e-3:
            self.state = State.IDLE
        else:
            self.state = State.FLYING
        self.body_rect = PhysicalRect(*self.body.position - (self.width / 2, self.height / 2), self.width, self.height)

    @property
    def position(self):
        return self.body.position - (self.width / 2, self.height / 2)

    def __view__(self, camera):
        """
        Рисует сущность на экране
        :param camera:
        :return:
        """
        # Прямоугольник проекции игрока на поверхость камеры
        rect_for_camera: pygame.Rect = camera.projection_of_rect(self.body_rect)

        # Если не пересекается с экраном, то не рисуем
        if not rect_for_camera.colliderect(camera.screen.get_rect()):
            return

        # Рисуем серый прямоугольник и прекращаем рисование, если нет спрайта
        # TODO: Сделать спрайт по умолчанию, чтобы убрать это
        if self.base_image is None:
            camera.project_rect(self.body_rect, (100, 100, 100))
            return

        # Если преобразованный спрайт считался для другой дистанции от камеры до сцены
        # То пересчитываем его
        if self.last_camera_distance != camera.distance:
            self.scaled_image = pygame.transform.scale(self.base_image, rect_for_camera.size)
            self.last_camera_distance = camera.distance

        # Рисуем спрайт игрока
        camera.temp_surface.blit(self.scaled_image, rect_for_camera)

    def __devview__(self, camera):
        super(Entity, self).__devview__(camera)
        camera.temp_surface.blit(
            pygame.transform.flip(pygame.font.SysFont("Arial", 20).render(str(self.body.position), True, (255, 0, 0)),
                                  False, True), (0, 0))

        camera.temp_surface.blit(
            pygame.transform.flip(
                pygame.font.SysFont("Arial", 20).render(str(self.body.shapes.pop().get_vertices()), True, (255, 0, 0)),
                False, True), (0, 50))

        camera.temp_surface.blit(
            pygame.transform.flip(
                pygame.font.SysFont("Arial", 20).render(str(self.body.angle), True, (255, 0, 0)),
                False, True), (0, 100))
