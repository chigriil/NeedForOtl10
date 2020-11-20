import pygame

from Engine.Scene.entities import Player
from Engine.Scene.gamescene import Scene, Background


class TestLevel(Scene):
    def __init__(self, gameapp):
        super(TestLevel, self).__init__(gameapp)
        self.subjects = []  # Предметы на игровом поле, например летающие ножи, частицы и т.д.
        self.entities = [Player(x=i) for i in range(10)]  # Живые сущности, например игрок и враги
        self.bgpicture = pygame.image.load('Resources/pictures/108d19ec.jpeg')
        self.bg = Background()

    def draw(self, camera):
        camera.view(self.bg)
        for sub in self.subjects:
            pass
        for ent in self.entities:
            camera.view(ent)

    def step(self, dt):
        for sub in self.subjects:
            sub.step(dt)
        for ent in self.entities:
            ent.step(dt)
