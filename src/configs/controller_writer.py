from Engine.utils.utils import *
import pygame

"""
Порядок эвентов;
Бросок
Удар
Идти влево
Идти вправо
Бег
Прыжок
"""

save_yaml([pygame.K_q, pygame.K_v, pygame.K_a, pygame.K_d, pygame.K_LSHIFT, pygame.K_SPACE],
          'controllers/config_wasd.yaml')
