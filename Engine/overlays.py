"""
Модуль с различными оверлеями
Возможно удалиться в будующих версиях
"""
from typing import Any
from pygame import Rect
import pygame
from collections import deque


class Overlay:
    """
    Класс оверлея
    Нужен наприммер для вивода ФПС, отладочной информации
    Полосок здоровья и прочего
    """

    def __init__(self, screen: pygame.Surface, data_source: Any):
        """
        Оверлеи будут вызываться дл яотриосвки в отдельном методе в MicroApp
        :param screen: поверхность, на которой будет рысоваться (скорее всего экран)
        :param data_source: источник данных для оверлея (может быть всё что угодно
        """
        self.screen = screen
        self.data_source = data_source

    def update(self, dt):
        """
        Эволюция оверлея во времени, например для некой анимации или внутреней логики
        :param dt: квант времени
        :return:
        """
        pass

    def draw(self):
        """
        Отрисовывает оверлей на экране
        :return:
        """


class FPS(Overlay):
    """
    Счётчик фпс
    """
    def __init__(self, screen, clock, x=30, y=10, width=95, height=30, buffer=30, update_period=0.5):
        super(FPS, self).__init__(screen, clock)

        self.text_rect = Rect(x, y, width, height)

        self.font = pygame.font.SysFont('Arial', int(height))

        self.frame_times = deque()

        self.buffer = buffer

        self.fps = 100

        self.update_period = update_period

        self.time_after_last_fps_update = 0

    def update(self, dt):
        # Некая фильтрация медианным фильтром
        self.time_after_last_fps_update += dt

        self.frame_times.append(self.data_source.get_fps())
        if len(self.frame_times) > self.buffer:
            self.frame_times.popleft()

        if self.time_after_last_fps_update > self.update_period:
            self.time_after_last_fps_update = 0
            self.fps = sum(self.frame_times) / len(self.frame_times)

    def draw(self):
        text = self.font.render('{:.1f} FPS'.format(self.fps), True, (255, 0, 0))
        self.screen.blit(text, text.get_rect(midright=self.text_rect.midright).topleft)
