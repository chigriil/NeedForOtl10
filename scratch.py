from settings import *
from src.Levels.testlevel import *
from src.game import Game

pygame.font.init()
pygame.mixer.pre_init()
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

attrs = {'x': object.x, 'y': object.y, 'widt': object.width, 'height': object.height,
                         'sprite': object.sprite, 'physical_space': object.physical_space,
                         'angle': object.angle}

with open(username + '_save', 'w'):
    for object in self.objects:
        attrs = ['x', 'y', 'width', 'height',
                 'sprite', 'physical_space',
                 'angle']
        attr_final = {}
        for attr in attrs:
            if hasattr(object, attr):
                attr_final[attr] = object.__dict__[attr]
            else:
                attr_final[attr] = None

self.x, self.y, self.width, self.height, self.sprite, self.physical_space,
               self.body, self.shape, self.angle, self.mass, self.moment, self.elasticity, self.friction, self.type_

return '{}{}{}{}{}{}{}{}{}{}{}{}{}{}'.format(self.__class__.__name__, self.width, self.height, self.sprite, self.physical_space,
               self.body, self.shape, self.angle, self.mass, self.moment, self.elasticity, self.friction, self.type_)