"""
Отвечающий за симулицию
100% поменяется в будущих версиях
"""

import numpy as np
import pygame
import pymunk
from pygame.draw import rect, circle

from Engine.Scene.physical_primitives import PhysicalRect
from src.persons import Player

GRAVITY = np.array([0, -9.81])


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


class GameEvent:
    """
    Класс игровый событий, вызываемых по условию
    """

    def __init__(self, condition, action):
        """
        :param condition: условия срабатывания
        :param action: действие
        """
        self.contition = condition
        self.action = action

    def hadle(self):
        if self.contition():
            self.action()


class Scene:
    """
    Класс игровой сцены, он же симулиция
    На основе сцены будут делаться уровни
    TODO: придумать систему ИГРОВЫХ событий, вызывающихся, в зависимости от услових
    TODO: например, по времени, здоровью игрока, от рандома, от колва очков игрока
    TODO: придумать, как сохранять состояние уровня
    """

    def __init__(self, game_app, background=SunnyField(), border=PhysicalRect(-10, -5, 20, 10)):
        """
        :param game_app: приложение игры, нужно для управления сценой
        """
        self.game_app = game_app
        # Игровые события
        self.game_events: list[GameEvent] = []
        # Предметы на игровом поле, например летающие ножи, частицы и т.д.
        self.objects = []
        # Живые сущности, например враги
        self.entities = []
        # Задний фон
        self.bg = background

        # Сама физика
        # физическое пространство
        self.physical_space = pymunk.Space()
        self.physical_space.gravity = GRAVITY

        # Граница уровня
        self.border = border
        top = pymunk.Segment(self.physical_space.static_body, self.border.topleft, self.border.topright, 0)
        bottom = pymunk.Segment(self.physical_space.static_body, self.border.bottomright, self.border.bottomleft, 0)
        right = pymunk.Segment(self.physical_space.static_body, self.border.topright, self.border.bottomright, 0)
        left = pymunk.Segment(self.physical_space.static_body, self.border.bottomleft, self.border.topleft, 0)

        bottom.friction = 1  # трение на полу

        self.physical_space.add(top)
        self.physical_space.add(bottom)
        self.physical_space.add(right)
        self.physical_space.add(left)

    def __view__(self, camera):
        """
        Отрисовка
        :param camera: камера, на поверхности которой рисуем
        :return:
        """
        camera.view(self.bg)
        for sub in self.objects:
            camera.view(sub)
        for ent in self.entities:
            camera.view(ent)

    def __devview__(self, camera):
        """
        Отрисовка параметров для разработчиков
        :param camera: камера, на поверхности которой рисуем
        :return:
        """
        camera.devview(self.bg)
        for sub in self.objects:
            camera.devview(sub)
        for ent in self.entities:
            camera.devview(ent)

        # координатные оси
        camera.project_line(np.array([0, -100]), np.array([0, 100]), (0, 0, 255), 3)
        camera.project_line(np.array([-100, 0]), np.array([100, 0]), (255, 0, 0), 3)

        # Границы уровня
        camera.project_line(
            self.border.topleft,
            self.border.topright,
            (139, 69, 19),
            3
        )

        camera.project_line(
            self.border.topright,
            self.border.bottomright,
            (139, 69, 19),
            3
        )

        camera.project_line(
            self.border.bottomright,
            self.border.bottomleft,
            (139, 69, 19),
            3
        )

        camera.project_line(
            self.border.bottomleft,
            self.border.topleft,
            (139, 69, 19),
            3
        )

    def step(self, dt):
        """
        Эволюция системы во времени
        :param dt: квант времени
        :return:
        """
        for game_event in self.game_events:
            game_event.hadle()

        # Расчёт физики
        self.physical_space.step(dt)

        for sub in self.objects:
            sub.step(dt)
        for ent in self.entities:
            ent.step(dt)


class Level(Scene):
    """
    Класс игрового уровня
    TODO: добавить методы сохранения и считывания из файла
    """

    def __init__(self, game_app, background=SunnyField(), border=PhysicalRect(-10, -5, 20, 10)):
        super(Level, self).__init__(game_app, background, border)

        # Выносим игрока отдельно, чтобы был удобный доступ к нему
        # Возможно так придётся вынести и антогонистов
        # Инициализируется в отдельном методе init_player
        self.player = None

    def init_player(self, x=0, y=0, width=0.9, height=1.8, sprite=None, animations_config=None):
        """
        Инициализирует игрока
        :param x:
        :param y:
        :param width:
        :param height:
        :param sprite:
        :param animations_config:
        :return:
        """
        self.player = Player(self.physical_space, x, y, width, height, sprite)
        self.player.load_animations(animations_config)
        self.entities.append(self.player)

    def step(self, dt):
        super(Level, self).step(dt)

        # Возвращаем игрока в границы уровня
        self.player.check_scene_border(self.border)

    def __devview__(self, camera):
        super(Level, self).__devview__(camera)

        # Всякий текст, который передет в класс оверлея
        camera.temp_surface.blit(
            pygame.transform.flip(
                pygame.font.SysFont("Arial", 20).render(str(self.player.body.position), True, (255, 0, 0)),
                False, True), (0, 0))

        camera.temp_surface.blit(
            pygame.transform.flip(
                pygame.font.SysFont("Arial", 20).render(str(self.player.body.shapes.pop().get_vertices()), True,
                                                        (255, 0, 0)),
                False, True), (0, 50))

        camera.temp_surface.blit(
            pygame.transform.flip(
                pygame.font.SysFont("Arial", 20).render(
                    f'{self.player.state}, {self.player.horizontal_view_direction}, {self.player.vertical_view_direction}',
                    True,
                    (255, 0, 0)),
                False, True), (0, 75))
