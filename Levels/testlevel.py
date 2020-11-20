"""
Тестовый уровень для нужд програмистов
TODO: чем-нибудь напольникть уровень
"""
import pygame

from Engine.Scene.entities import Player
from Engine.Scene.gamescene import Scene, SunnyField


class TestLevel(Scene):
    def __init__(self, game_app):
        super(TestLevel, self).__init__(game_app)
        self.entities = [Player(x=i, img=pygame.image.load('Levels/Boxer2_Idle_000.png')) for i in range(10)]
        self.bg_picture = pygame.image.load('Resources/pictures/108d19ec.jpeg')
        self.bg = SunnyField()
