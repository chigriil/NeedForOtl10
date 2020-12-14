"""
Тут храняться классы игрока и антогонистов
TODO: Подобрать более подходлящитее имя файлу
"""
import os

from pymunk import Space

from Engine.EntityControllers import ManualController
from Engine.Scene.entities import Entity
from Engine.utils.utils import load_yaml
from settings import person_configs_path

# Реестр всех персонажей
PersonRegistry = {}


class BaseCharacter(Entity):
    """
    Базовый класс игрового персонажа
    На основе него делаются остальные классы
    """
    configs = load_yaml('src/configs/persons/maincharacter.yaml')

    def __init__(self, physical_space: Space, x=0, y=0, brain=ManualController):
        super(BaseCharacter, self).__init__(physical_space, x, y, brain=brain, **self.configs)

    def save_data(self):
        return {'class': self.name, 'vector': list(self.position), 'brain': self.brain.__class__.__name__}

    def __init_subclass__(cls, **kwargs):
        PersonRegistry[cls.__name__] = cls


def make_character(configs):
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
    return type(configs['name'], (BaseCharacter,), {'configs': configs})


# Загрузка персонажей
for person_config_file in os.listdir(person_configs_path):

    if not person_config_file.endswith('.yaml'):
        continue

    config = load_yaml(os.path.join(person_configs_path, person_config_file))

    make_character(config)
