"""
Модуль с различными оверлеями
Возможно удалиться в будующих версиях
"""
from collections import deque
from typing import Any

import pygame
from pygame import Rect

from Engine.Scene.states import State
from settings import SCREEN_HEIGHT


class Overlay:
    """
    Класс оверлея
    Нужен наприммер для вивода ФПС, отладочной информации
    Полосок здоровья и прочего
    """

    def __init__(self, screen: pygame.Surface, data_source: Any, font_size=30):
        """
        Оверлеи будут вызываться дл яотриосвки в отдельном методе в MicroApp
        :param screen: поверхность, на которой будет рысоваться (скорее всего экран)
        :param data_source: источник данных для оверлея (может быть всё что угодно
        :param font_size: относительный размер шрифта, реальный считается по формуле
        int(font_size / 900 * self.screen.get_height()
        """
        self.screen = screen
        self.data_source = data_source
        self.font = pygame.font.SysFont('Arial', int(font_size / 900 * self.screen.get_height()))

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


class HealthBar(Overlay):
    def __init__(self, screen, clock, entity, camera, left=True):
        super(HealthBar, self).__init__(screen, clock)

        width = self.screen.get_width() * 22 // 48
        height = self.screen.get_height() * 3 // 48

        self.entity = entity

        self.camera = camera

        self.entity.full_health = self.entity.health

        self.font = pygame.font.SysFont('Ariel', height)

        self.text = self.font.render(str(self.entity.health), True, (0, 0, 0))

        self.fps = 10

        self.left = left

        if self.left:
            self.health_rect = pygame.Rect(int(self.screen.get_width() * 1 / 48),
                                           int(self.screen.get_height() * 3 / 48),
                                           width, height)
            self.outer_health_rect = pygame.Rect(
                (int(self.screen.get_width() * 1 / 48), int(self.screen.get_height() * 3 / 48),
                 width, height))
        else:
            self.health_rect = pygame.Rect(int(self.screen.get_width() * 1 / 48),
                                           int(self.screen.get_height() * 3 / 48),
                                           width, height)
            self.outer_health_rect = pygame.Rect(
                (int(self.screen.get_width() * 25 / 48), int(self.screen.get_height() * 3 / 48),
                 width, height))

    def draw(self):
        self.text = self.font.render(str(round(self.entity.health, 0)), True, (0, 0, 0))

        self.health_rect.w = int(self.outer_health_rect.w * self.entity.health / self.entity.full_health)
        pygame.draw.rect(self.screen, (138, 3, 3), self.health_rect)
        pygame.draw.rect(self.screen, (255, 0, 0), self.outer_health_rect, 3)

        if self.left:
            self.screen.blit(self.text, (self.health_rect.x + self.health_rect.w // 2 -
                                         self.text.get_width() // 2,
                                         self.health_rect.y + self.health_rect.h // 2 - self.text.get_height() // 2))
        else:
            self.screen.blit(self.text, (self.health_rect.x + self.health_rect.w // 2 -
                                         self.text.get_width() // 2,
                                         self.health_rect.y + self.health_rect.h // 2 - self.text.get_height() // 2))
            self.health_rect.x = self.outer_health_rect.x + self.outer_health_rect.w - self.health_rect.w


class CoolDownOverlay(Overlay):
    def __init__(self, screen, clock, coolodowns: list, x=0, y=0, width=50, height=30):
        super(CoolDownOverlay, self).__init__(screen, clock)

        self.width = width

        self.height = height

        self.cooldowns = coolodowns

        self.rects = []

        self.texts = []

    def update(self, dt):
        for i, rect in enumerate(self.rects):
            rect.w = int(min(self.width, self.cooldown))

    def draw(self):
        for rect in self.rects:
            pygame.draw.rect(self.screen, (167, 167, 167), rect)
        for i, text in enumerate(self.texts):
            self.screen.blit(text, self.text_pos[i])


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


class SaveButton(Button):
    def __init__(self, screen, clock, x=0, y=0, width=95, height=30):
        super(SaveButton, self).__init__(screen, clock)

        self.button_rect = Rect(x, y, width, height)

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


class DevMode(Overlay):
    def __init__(self, screen, game):
        super(DevMode, self).__init__(screen, game, 25)
        self.digits = 2

    def draw(self):
        if not self.data_source.DEVMODE:
            return

        player = self.data_source.scene.player

        player_position = player.body.position

        player_velocity = player.body.velocity

        camera_position = self.data_source.camera.position

        data_left = {
            'Player position': f'{round(player_position[0], self.digits)}, {round(player_position[1], self.digits)}',
            'Player velocity': f'{round(player_velocity[0], self.digits)}, {round(player_velocity[1], self.digits)}',
            'Player state': player.state,
            'Player vertical view direction': player.vertical_view_direction,
            'Player horizontal view direction': player.horizontal_view_direction,
            'Player can lean on feet': player.can_lean_on_feet(),
            'Player health': player.health,
        }

        enemy_health = {
            f'Enemy {number} ({entity.__class__.__name__}) health': entity.health
            for number, entity in enumerate(self.data_source.scene.entities)
        }

        data_left |= enemy_health

        data_right = {
            'Camera position': f'{round(camera_position[0], self.digits)}, {round(camera_position[1], self.digits)}',
            'Camera distance': f'{round(self.data_source.camera.distance)}',
            'Operator target': 'yes' if self.data_source.camera_operator.target is not None else 'no',
            'Operator type': self.data_source.camera_operator.targeting_method.value,
            'Operator aiming': self.data_source.camera_operator.aiming,
            'Number of objects': len(self.data_source.scene.objects),
            'Number of entities': len(self.data_source.scene.entities),
            'Number of physical bodies': len(self.data_source.scene.physical_space.bodies),
            'Number of physical shapes': len(self.data_source.scene.physical_space.shapes)
        }

        for pos, (key, value) in enumerate(data_left.items()):
            self.screen.blit(
                self.font.render(f'{key}: {value}', True, (255, 255, 0)),
                (self.screen.get_width() / 40, self.screen.get_height() / 1.8 + pos * self.font.get_height() * 1.2)
            )

        for pos, (key, value) in enumerate(data_right.items()):
            self.screen.blit(
                self.font.render(f'{key}: {value}', True, (255, 255, 0)),
                (self.screen.get_width() - self.screen.get_width() / 4,
                 self.screen.get_height() / 1.8 + pos * self.font.get_height() * 1.2)
            )


class WinHandler(Overlay):
    def __init__(self, screen, scene):
        super(WinHandler, self).__init__(screen, scene, SCREEN_HEIGHT / 5)
        self.text = None

    def update(self, dt):
        try:
            if self.data_source.player.state == State.WIN:
                self.text = 'LEFT WON!'

            if self.data_source.entities[0].state == State.WIN:
                self.text = 'RIGHT WON!'
        except IndexError:
            pass

    def draw(self):
        if self.text is not None:
            text_surf = self.font.render(self.text, True, (255, 255, 0))
            self.screen.blit(text_surf, text_surf.get_rect(center=self.screen.get_rect().center).topleft)
