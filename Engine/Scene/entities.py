"""
Модуль реализующий классы живых сущностей
Например игрока и врагов
"""
import numpy as np
import pygame
from pygame import Surface
from pygame.draw import rect

from .physical_primitives import PhysicalRect


class Entity:
    """
    Базовый класс сущности
    """

    def step(self, dt):
        """
        Реализует эволюцию сущности во времени
        :param dt: квант времени
        :return:
        """
        pass

    def __view__(self, camera):
        """
        Рисует сущность на экране
        :param camera:
        :return:
        """
        pass


class Player(Entity):
    """
    Класс игрока
    TODO: прикрутить атрибуты игрока, например здоровье, уклонение, и т.д.
    TODO: добавить объект кулаков и ног, чтобы можно было легко реализовать засчитывание урона
    TODO: очень желателдьно добавить подсчёт очков, нужно если вруг мы решим завести ии от OpenAI
    TODO: придумать, как сериализовать игрока и как делать конфиг
    TODO: прикрутить анимацию удара
    TODO: прикрутить анимацию кидани
    TODO: придумать, как сохранять состояние игрока
    """

    def __init__(self, x=0, y=0, height=1.8, width=0.7, img: Surface = None):
        """
        :param x: x координата левого нижнего края игрока
        :param y: y координата левого нижнего края игрока
        :param height: высота игрока
        :param width: ширина игрока
        :param img: спрайт игрока
        TODO: разделить толо игрока на само тело, ноги, руки, голову (нужно для удобной анимации ударов)
        """
        # Координаты левого нижнего края игрока
        self.__position = np.array([float(x), float(y)])
        # Высота игрока
        self.height = height
        # Ширина игрока
        self.width = width
        # Хитбокс тела, на него нятигивается спрайт тела
        self.body_rect = PhysicalRect(*self.__position, self.width, self.height)

        # Оригинальтная картинка спрайта
        self.base_image = pygame.transform.flip(img, False, True)

        # Преобразованное изображения спрайта
        # Имеет размер, как проекция игрока на поверхность камеры
        # Нужно для оптимизации
        self.image = self.base_image
        # Дистанция от камеры да сцены
        self.last_camera_distance = -1

        # Конечно, игрока можно проецировать на несколько камер
        # Можно хранить несколько спрайтов для разных дистанций, но зачем
        # Если всегда на игрпока будет смотреть лишь одна камера

    def __view__(self, camera):

        # Прямоугольник проекции игрока на поверхость камеры
        rect_for_camera: pygame.Rect = camera.projection_of_rect(self.body_rect)

        # Если не пересекается с экраном, то не рисуем
        if not rect_for_camera.colliderect(camera.screen.get_rect()):
            return
        # Рисуем серый прямоугольник, если нет спрайта
        # TODO: Сделать спрайт по умолчанию, чтобы убрать это
        rect(camera.temp_surface, (100, 100, 100), rect_for_camera)

        # Если нет спрайта игрока
        if self.base_image is None:
            return

        # Если преобразованный спрайт считался для другой дистанции от камеры до сцены
        # То пересчитываем его
        if self.last_camera_distance != camera.distance:
            self.image = pygame.transform.scale(self.base_image, rect_for_camera.size)

        # Рисуем спрайт игрока
        camera.temp_surface.blit(self.image, rect_for_camera)
