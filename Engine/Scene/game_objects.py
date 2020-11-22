from typing import Union

import pygame
import pymunk
from pymunk import Vec2d

from Engine.Scene.physical_primitives import PhysicalRect


class GameObject:
    def __init__(self, x, y, width=0.3, height=0.3, sprite=None):
        self._position = Vec2d(x, y)
        self.width = width
        self.height = height
        self.sprite = sprite
        if self.sprite is not None:
            # Переворачиваем спрайт
            self.sprite = pygame.transform.flip(self.sprite, False, True)

        self.body_rect = PhysicalRect(x, y, width, height)

        self.scaled_sprite = self.sprite
        self.last_camera_distance = -1

    def step(self, dt):
        pass

    def __view__(self, camera):

        # Проекция описанного прямоугольника на камеру
        rect_for_camera: pygame.Rect = camera.projection_of_rect(self.body_rect)

        # Если не пересекается с экраном, то не рисуем
        if not rect_for_camera.colliderect(camera.screen.get_rect()):
            return

        # Рисование спрайта
        # Рисуем серый прямоугольник и прекращаем рисование, если нет спрайта
        if self.sprite is None:
            camera.project_rect(self.body_rect, (100, 100, 100))
            return

        # Если преобразованный спрайт считался для другой дистанции от камеры до сцены
        # То пересчитываем его
        if self.last_camera_distance != camera.distance:
            self.scaled_sprite = pygame.transform.scale(self.sprite, rect_for_camera.size)
            self.last_camera_distance = camera.distance

        # Рисуем спрайт игрока
        camera.temp_surface.blit(self.scaled_sprite, rect_for_camera)

    def __devview__(self, camera):
        camera.dev_rect(self.body_rect, (255, 0, 0), 5)
        camera.project_point(self.position, 7)  # позиция объекта

    @property
    def position(self):
        return self._position


class StaticRectangularObject(GameObject):
    def __init__(self, x, y, width=0.3, height=0.3, sprite=None,
                 physical_space=None, mass=1, type_=pymunk.Body.STATIC):
        super(StaticRectangularObject, self).__init__(x, y, width, height, sprite)
        self.type_ = type_
        self.physical_space: pymunk.Space = physical_space
        self.mass: Union[float, int] = mass

        moment = pymunk.moment_for_box(self.mass, (self.width, width))
        self.body: pymunk.Body = pymunk.Body(self.mass, moment, pymunk.Body.STATIC)
        self.body.position = (x + width / 2, y + height / 2)
        self.body_shape: pymunk.Shape = pymunk.Poly.create_box(self.body, (self.width, self.height))
        self.body_shape.elasticity = 0
        self.physical_space.add(self.body, self.body_shape)

    def step(self, dt):
        self.body_rect = PhysicalRect(*(self.body.position - (self.width / 2, self.height / 2)),
                                      self.width, self.height)
