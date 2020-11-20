import numpy as np
from pygame.draw import rect, circle


class Background:
    def __init__(self):
        pass

    def __view__(self, camera):
        if camera.position[1] ** 2 - camera.window_height ** 2 / 4 < 0:
            sky_rect = np.array([
                0,
                (camera.window_height / 2 - camera.position[1]),
                camera.window_width,
                (camera.window_height / 2 + camera.position[1]),
            ]) * camera.scale_factor

            ground_rect = np.array([
                0,
                0,
                camera.window_width,
                (camera.window_height / 2 - camera.position[1]),
            ]) * camera.scale_factor

            rect(camera.tempsurface, (135, 206, 250), sky_rect)
            rect(camera.tempsurface, (34, 139, 34), ground_rect)

        elif camera.camera_rect[1] > 0:
            rect(camera.tempsurface, (135, 206, 250), camera.tempsurface.get_rect())

        elif camera.camera_rect[1] < 0:
            rect(camera.tempsurface, (34, 139, 34), camera.tempsurface.get_rect())

        pt = camera.projection_of_point(np.array([2, 5]))
        circle(camera.tempsurface, (255, 255, 0), pt, camera.projection_of_length(1))




class Scene:
    def __init__(self, gameapp):
        self.gameapp = gameapp

    def draw(self, camera):
        pass

    def step(self, dt):
        pass
