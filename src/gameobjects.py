import os

import pymunk
from pymunk import Body

from Engine.Scene.game_objects import PhysicalGameObject, ObjectRegistry
from Engine.utils.physical_primitives import PhysicalRect
from Engine.utils.utils import load_yaml, load_image, pil_to_pygame
from settings import game_objects_configs_path


class RectangularObject(PhysicalGameObject):
    configs = load_yaml('src/configs/game_objects/fridge.yaml')

    def __init__(self, scene, x, y, angle=0, type_=Body.STATIC):
        sprite = None
        if self.configs['sprite'] is not None:
            sprite = pil_to_pygame(load_image(self.configs['sprite']))

        super(RectangularObject, self).__init__(x, y, angle=angle, sprite=sprite, scene=scene,
                                                type_=type_, **self.configs['init'])

    def save_data(self):
        print(self.position)
        return {
            'type': self.body.body_type,
            'x': self.position.x,
            'y': self.position.y,
            'angle': self.body.angle
        }


class CircularObject(PhysicalGameObject):
    configs = load_yaml('src/configs/game_objects/alarm_clock.yaml')

    def __init__(self, scene, x, y, angle=0, type_=Body.STATIC):

        sprite = None
        if self.configs['sprite'] is not None:
            sprite = pil_to_pygame(load_image(self.configs['sprite']))

        init_config: dict = self.configs['init']

        radius = init_config['radius']

        if init_config['moment'] is None:
            init_config['moment'] = pymunk.moment_for_circle(init_config['mass'], 0, radius)

        body = pymunk.Body(init_config['mass'], init_config['moment'])
        shape = pymunk.Circle(body, radius)

        super(CircularObject, self).__init__(x=x, y=y, width=radius, height=radius,
                                             scene=scene, sprite=sprite,
                                             body=body, shape=shape, angle=angle,
                                             mass=init_config['mass'], moment=init_config['moment'],
                                             elasticity=init_config['elasticity'],
                                             friction=init_config['friction'], type_=type_)

        self.body_rect = PhysicalRect(x - radius / 2, y - radius / 2, 2 * radius, 2 * radius)

    def no_sprite_view(self, camera):
        camera.project_circle(self.boundingbox2.centre, self.body_shape.radius, (100, 100, 100))

    def save_data(self):
        return {
            'type': self.body.body_type,
            'x': self.position.x,
            'y': self.position.y
        }


def make_object(configs):
    """
    Создает класс сущности с нужными параметрами
    была претензия на метакласс, но он тут не особо нужен
    :param configs: конфигурация сущности
    У файла должна ьыть следующая структура
    ##################################################
    name: 'Danilio'
    description: null
    width: 0.96
    height: 1.8
    mass: 75
    animations: 'Resources/Animations/DanyaPers.yaml'
    ##################################################
    :return: None
    """
    # Создаём класс персонажа
    return type(configs['name'], (ObjectRegistry[configs['type']],), {'configs': configs})


def init_object():
    len_0 = len(ObjectRegistry)

    for game_object_config_file in os.listdir(game_objects_configs_path):

        if not game_object_config_file.endswith('.yaml'):
            continue

        config = load_yaml(os.path.join(game_objects_configs_path, game_object_config_file))

        print(f'Loading {config["name"]}')
        make_object(config)
    return len(ObjectRegistry) - len_0


def register():
    new_objects = init_object()
    print(f'Registered {len(ObjectRegistry) - new_objects} objects')
