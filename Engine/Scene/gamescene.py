"""
Отвечающий за симулицию
100% поменяется в будущих версиях
"""
import numpy as np
from pygame.draw import rect, circle

from settings import DEVMODE


class Background:
    """
    Класс заднего фона
    по идее просто замыленная фотка
    """

    def __view__(self, camera):
        """
        Проекция заднего фона на камеру
        :param camera:
        :return:
        """
        ...


class SunnyField(Background):
    """
    Класс простого заднего фона
    Солнце + небо + земля
    Горизонт на линии y = 0
    """

    def __init__(self):
        pass

    def __view__(self, camera):

        # Проверка, пересекает ли плоскость камеры горизонт
        # Если пересекает
        if camera.position[1] ** 2 - camera.window_height ** 2 / 4 < 0:
            # Прямоугольник неба
            sky_rect = np.array([
                0,
                (camera.window_height / 2 - camera.position[1]),
                camera.window_width,
                (camera.window_height / 2 + camera.position[1]),
            ]) * camera.scale_factor

            # Прямоугольник земли
            ground_rect = np.array([
                0,
                0,
                camera.window_width,
                (camera.window_height / 2 - camera.position[1]),
            ]) * camera.scale_factor

            # Рисование
            rect(camera.temp_surface, (135, 206, 250), sky_rect)
            rect(camera.temp_surface, (34, 139, 34), ground_rect)

        # Камера выше горизонта
        elif camera.camera_rect.y > 0:
            # Заливаем экран небом
            rect(camera.temp_surface, (135, 206, 250), camera.temp_surface.get_rect())

        # Камера ниже горизонта
        elif camera.camera_rect.y < 0:
            # Заливаем экран землёй
            rect(camera.temp_surface, (34, 139, 34), camera.temp_surface.get_rect())

        # Рисекм солнце
        pt = camera.projection_of_point(np.array([2, 5]))
        circle(camera.temp_surface, (255, 255, 0), pt, camera.projection_of_length(1))


class Scene:
    """
    Класс игровой сцены, он же симулиция
    На основе сцены будут делаться уровни
    TODO: придумать систему ИГРОВЫХ событий, вызывающихся, в зависимости от услових
    TODO: например, по времени, здоровью игрока, от рандома, от колва очков игрока
    TODO: придумать, как сохранять состояние уровня
    """

    def __init__(self, game_app):
        """
        :param game_app: приложение игры, нужно для управления сценой
        """
        self.game_app = game_app
        # Предметы на игровом поле, например летающие ножи, частицы и т.д.
        self.subjects = []
        # Живые сущности, например игрок и враги
        self.entities = []
        # Задний фон
        self.bg = SunnyField()

    def draw(self, camera):
        """
        Отрисовка
        :param camera: камера, на поверхности которой рисуем
        :return:
        """
        camera.view(self.bg)
        for sub in self.subjects:
            camera.view(sub)
        for ent in self.entities:
            camera.view(ent)
        if DEVMODE:
            # координатные оси
            camera.project_line_on_camera(np.array([0, -100]), np.array([0, 100]), (0, 0, 255), 3)
            camera.project_line_on_camera(np.array([-100, 0]), np.array([100, 0]), (255, 0, 0), 3)

    def step(self, dt):
        """
        Эволюция системы во времени
        :param dt: квант времени
        :return:
        """
        for sub in self.subjects:
            sub.step(dt)
        for ent in self.entities:
            ent.step(dt)
