"""
Тестовый уровень для нужд програмистов
TODO: чем-нибудь напольникть уровень
"""
import pygame
import pymunk

from Engine.Scene.game_objects import StaticRectangularObject, DynamicRectangularObject, DynamicCircularObject
from Engine.Scene.gamescene import Scene, SunnyField
from Engine.Scene.physical_primitives import PhysicalRect
from src.persons import Player


class TestLevel(Scene):
    def __init__(self, game_app):
        super(TestLevel, self).__init__(game_app, PhysicalRect(-16, -9, 32, 18))
        self.bg = SunnyField()

        self.player = Player(self.physical_space, 0, 0.1, sprite=pygame.image.load('src/Levels/Boxer2_Idle_000.png'))
        self.player.load_animations('src/Levels/test.yaml')

        self.entities.append(self.player)

        # граница горизонта (чтобы человек не проваливался под землю)
        hl = pymunk.Segment(self.physical_space.static_body,
                            (self.border.x, 0),
                            (self.border.x + self.border.width, 0),
                            0)
        hl.friction = 1
        self.physical_space.add(hl)

        self.objects.append(StaticRectangularObject(2, 0, 1, 0.7, sprite=pygame.image.load('src/Levels/monalisa.jpg'),
                                                    physical_space=self.physical_space))
        self.objects.append(
            DynamicRectangularObject(2, 3, 1, 0.7, sprite=pygame.image.load('src/Levels/monalisa.jpg').convert_alpha(),
                                     physical_space=self.physical_space))

        self.objects.append(DynamicRectangularObject(2, 5, 1, 0.7, physical_space=self.physical_space, angle=0.8))
        self.objects.append(DynamicCircularObject(1, 5, 0.7, physical_space=self.physical_space))
        self.objects.append(DynamicCircularObject(1, 5, 0.7, physical_space=self.physical_space,
                                                  sprite=pygame.image.load(
                                                      'src/Levels/582ab5e93efcb_smaylik.png').convert_alpha()))

    def step(self, dt):
        """
        Эволюция системы во времени
        :param dt: квант времени
        :return:
        """
        for game_event in self.game_events:
            game_event.hadle()

        self.physical_space.step(dt)

        for sub in self.objects:
            sub.step(dt)
        for ent in self.entities:
            ent.step(dt)

        self.player.check_scene_border(self.border)

    def __devview__(self, camera):
        super(TestLevel, self).__devview__(camera)

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
