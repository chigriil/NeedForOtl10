from math import pi, tan, atan

import numpy as np
import pygame
from pygame.draw import circle, line

from settings import SCREEN_HEIGHT, SCREEN_WIDTH, DEVMODE


class Camera:
    def __init__(self, screen: pygame.Surface, x=0, y=0, h_fov=pi / 2, distance=15):
        self.screen = screen
        self.tempsurface = pygame.Surface(screen.get_rect().size)
        self.__position = np.array([float(x), float(y)])
        self.h_fov = h_fov

        self.v_fov = None  # h_fov * SCREEN_HEIGHT / SCREEN_WIDTH
        self.__distance = None
        self.window_width = None
        self.window_height = None
        # Коэффициент, на который умножаются координаты, чтобы отрисовать объекты на экране на экране
        self.scale_factor = None
        self.camera_rect = None
        self.distance = distance
        self.devfont = pygame.font.SysFont(pygame.font.get_fonts()[0], 50)

    def view(self, gameobject):
        gameobject.__view__(self)

    def show(self):
        # Отражение по оси y, потомучто лень писать преобразования координат вообще везде
        # Предлагаю оставить это как есть
        # TODO: Если кто хочет сделайте нормально, т.к трансформации отнимают осень много фпс
        if DEVMODE:
            self.DEVMODE_OVERLAY()

        self.screen.blit(pygame.transform.flip(self.tempsurface, False, True), (0, 0))
        # self.screen.blit(self.tempsurface,  (0, 0))
        self.tempsurface.fill((0, 0, 0))

    def DEVMODE_OVERLAY(self):
        tempsurfacerect = self.tempsurface.get_rect()
        self.project_line(np.array([0, -100]), np.array([0, 100]), (0, 0, 255), 3)
        self.project_line(np.array([-100, 0]), np.array([100, 0]), (255, 0, 0), 3)
        circle(self.tempsurface, (255, 0, 0), tempsurfacerect.center, 10)
        line(self.tempsurface, (255, 0, 0), tempsurfacerect.midleft, tempsurfacerect.midright)
        line(self.tempsurface, (255, 0, 0), tempsurfacerect.midtop, tempsurfacerect.midbottom)
        text_surf = self.devfont.render("Привет", True, (255, 255, 0))
        self.tempsurface.blit(text_surf, text_surf.get_rect().center)

    def projection_of_point(self, point):
        return (point + [self.window_width / 2 - self.__position[0],
                         self.window_height / 2 - self.__position[1]]) * self.scale_factor

    def projection_of_length(self, length):
        return length * self.scale_factor

    def project_line(self, start, end, color, width=1):
        line(self.tempsurface, color,
             self.projection_of_point(start),
             self.projection_of_point(end),
             width=width)

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, newposition):
        self.__position = newposition
        self.camera_rect = (
            self.__position[0] - self.window_width / 2,
            self.__position[1] - self.window_height / 2,
            self.window_width,
            self.window_height
        )

    @property
    def distance(self):
        return self.__distance

    @distance.setter
    def distance(self, newdistance):
        if newdistance <= 0:
            # raise CameraError("Distance became negative")
            return
        self.__distance = newdistance
        self.window_width = 2 * self.__distance * tan(self.h_fov / 2)
        self.window_height = self.window_width * SCREEN_HEIGHT / SCREEN_WIDTH
        self.v_fov = atan(self.window_height / self.__distance / 2)
        self.scale_factor = SCREEN_WIDTH / self.window_width
        self.camera_rect = (
            self.__position[0] - self.window_width / 2,
            self.__position[1] - self.window_height / 2,
            self.window_width,
            self.window_height
        )
        print('Width = {:.2f}\nHeight = {:.2f}\nDistance = {:.2f}\n'.format(self.window_width, self.window_height,
                                                                            self.__distance))
