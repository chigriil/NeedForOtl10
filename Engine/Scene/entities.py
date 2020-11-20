import numpy as np
from pygame.draw import rect


class Entity:
    def step(self, dt):
        pass


class Player(Entity):
    def __init__(self, x=0, y=0, height=1.8, width=0.7):
        self.__position = np.array([float(x), float(y)])
        self.height = height
        self.width = width

    def __view__(self, camera):
        position_on_camera = (self.__position - camera.position)
        rect_for_camera = np.array([
            position_on_camera[0] + camera.window_width / 2,
            position_on_camera[1] + camera.window_height / 2,
            self.width,
            self.height
        ]) * camera.scale_factor
        rect(camera.tempsurface, (100, 100, 100), rect_for_camera)
