import pygame
import pymunk


from Engine.Scene.game_objects import StaticRectangularObject, DynamicRectangularObject, DynamicCircularObject
from Engine.Scene.gamescene import SunnyField, Level
from Engine.Scene.physical_primitives import PhysicalRect

test_level_1 = Level(None, SunnyField(), PhysicalRect(-16, -9, 32, 18))
hl = pymunk.Segment(test_level_1.physical_space.static_body,
                            (test_level_1.border.x, 0),
                            (test_level_1.border.x + test_level_1.border.width, 0),
                            0)
hl.friction = 1

test_level_1.physical_space.add(hl)

test_level_1.load_level('hui')