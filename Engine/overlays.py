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


class Button(Overlay):
    def __init__(self, screen, clock, x=0, y=0, width=50, height=30):
        super(Button, self).__init__(screen, clock)

        self.button_rect = pygame.Rect(x, y, width, height)

        self.on = False

    def does(self):
        pass

    def activate(self, event):
        if self.button_rect.collidepoint(event.pos):
            self.on = True
            self.update(event)
            self.does()


class HealthBar(Overlay):
    def __init__(self, screen, clock, entity, camera, width=3, height=0.5):
        super(HealthBar, self).__init__(screen, clock)

        self.entity = entity

        self.camera = camera

        self.entity.health = 100

        self.health_rect = pygame.Rect(self.camera.projection_of_point(self.entity.body_rect.centre)[0],
                                       self.camera.projection_of_point(-1 * self.entity.body_rect.topleft[1] - 0.5)[1],
                                       self.camera.projection_of_length(width),
                                       self.camera.projection_of_length(height))

        self.font = pygame.font.SysFont('Arial', int(self.camera.projection_of_length(height)))

        self.text = self.font.render(str(self.entity.health), True, (0, 0, 0))

        self.fps = 10

    def draw(self):
        self.text = self.font.render(str(self.entity.health), True, (0, 0, 0))

        self.health_rect.center = (self.camera.projection_of_point(self.entity.body_rect.centre)[0],
                                   self.camera.projection_of_point(-1 * self.entity.body_rect.topleft[1] - 0.5)[1])

        pygame.draw.rect(self.screen, (138, 3, 3), self.health_rect)

        self.screen.blit(self.text, (self.health_rect.x + self.health_rect.w // 2 -
                                     self.text.get_width() // 2, self.health_rect.y))


class SaveButton(Button):
    def __init__(self, screen, clock, x=0, y=0, width=95, height=30):
        super(SaveButton, self).__init__(screen, clock)

        self.button_rect = Rect(x, y, width, height)

        self.font = pygame.font.SysFont('Arial', int(height))

        self.text = self.font.render('Save', True, (0, 0, 0))

        self.fps = 10

    def draw(self):
        self.button_rect.topright = (self.screen.get_width() * 46 / 48 + self.button_rect.w // 2,
                                     self.screen.get_height() * 2 / 48 - self.button_rect.h // 2)
        pygame.draw.rect(self.screen, (225, 0, 0), self.button_rect, 2)
        self.screen.blit(self.text, (self.button_rect.x + self.button_rect.w // 2 -
                                     self.text.get_width() // 2, self.button_rect.y))

    def update(self, event):
        if self.on:
            pass

    def does(self):
        """
        Для функции сохранения Юры
        :return:
        """
        print('Saved')


class PauseButton(Button):
    def __init__(self, screen, clock, x=0, y=0, width=95, height=30):
        super(PauseButton, self).__init__(screen, clock)

        self.button_rect = Rect(x, y, width, height)

        self.font = pygame.font.SysFont('Arial', int(height))

        self.text = self.font.render('Pause', True, (0, 0, 0))

        self.fps = 10

    def draw(self):
        self.button_rect.topright = (self.screen.get_width() * 46 / 48 + self.button_rect.w // 2,
                                     self.screen.get_height() * 5 / 48 - self.button_rect.h // 2)
        pygame.draw.rect(self.screen, (225, 0, 0), self.button_rect, 2)
        self.screen.blit(self.text, (self.button_rect.x + self.button_rect.w // 2 -
                                     self.text.get_width() // 2, self.button_rect.y))

    def does(self):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT))


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
