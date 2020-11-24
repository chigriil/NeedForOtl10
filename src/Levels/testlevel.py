"""
Тестовый уровень для нужд програмистов
TODO: чем-нибудь напольникть уровень
"""
import pygame
import pymunk

from Engine.Scene.game_objects import StaticRectangularObject, DynamicRectangularObject, GameObject
from Engine.Scene.gamescene import Scene, SunnyField
from Engine.Scene.physical_primitives import PhysicalRect
from src.persons import Player


class TestLevel(Scene):
    def __init__(self, game_app):
        super(TestLevel, self).__init__(game_app, PhysicalRect(-16, -9, 32, 18))
        self.bg = SunnyField()

        self.player = Player(self.physical_space, 0, 0.1, img=pygame.image.load('src/Levels/Boxer2_Idle_000.png'))

        self.entities.append(self.player)

        # ball_moment = pymunk.moment_for_circle(10, 0, 0.4)
        # self.ball = pymunk.Body(10, ball_moment)
        # self.ball.position = -1, 1
        #
        # self.ball_shape = pymunk.Circle(self.ball, 0.4)
        # self.ball_shape.elasticity = 0
        # self.ball_shape.friction = 1
        # self.physical_space.add(self.ball, self.ball_shape)

        hl = pymunk.Segment(self.physical_space.static_body,
                            (self.border.x, 0),
                            (self.border.x + self.border.width, 0),
                            0)
        hl.friction = 1
        self.physical_space.add(hl)

        self.objects.append(GameObject(1, 1, sprite=pygame.image.load('src/Levels/monalisa.jpg')))
        self.objects.append(StaticRectangularObject(2, 0, 1, 0.7, sprite=pygame.image.load('src/Levels/monalisa.jpg'),
                                                    physical_space=self.physical_space))
        self.objects.append(
            DynamicRectangularObject(2, 3, 1, 0.7, sprite=pygame.image.load('src/Levels/monalisa.jpg').convert_alpha(),
                                     physical_space=self.physical_space))

        self.objects.append(DynamicRectangularObject(2, 5, 1, 0.7, physical_space=self.physical_space, angle=0.8))

    def step(self, dt):
        """
        Эволюция системы во времени
        :param dt: квант времени
        :return:
        """
        for game_event in self.game_events:
            game_event.hadle()

        self.physical_space.step(dt)

        self.player.check_scene_border(self.border)
        for sub in self.objects:
            sub.step(dt)
        for ent in self.entities:
            ent.step(dt)

    def __view__(self, camera):
        """
        Отрисовка
        :param camera: камера, на поверхности которой рисуем
        :return:
        """
        super(TestLevel, self).__view__(camera)
        # circle(camera.temp_surface,
        #        (255, 255, 0),
        #        camera.projection_of_point(self.ball.position),
        #        camera.projection_of_length(self.ball_shape.radius))

    def __devview__(self, camera):
        super(TestLevel, self).__devview__(camera)

        camera.temp_surface.blit(
            pygame.transform.flip(pygame.font.SysFont("Arial", 20).render(str(self.player.body.position), True, (255, 0, 0)),
                                  False, True), (0, 0))

        camera.temp_surface.blit(
            pygame.transform.flip(
                pygame.font.SysFont("Arial", 20).render(str(self.player.body.shapes.pop().get_vertices()), True, (255, 0, 0)),
                False, True), (0, 50))

