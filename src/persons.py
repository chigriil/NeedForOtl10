"""
Тут храняться классы игрока и антогонистов
TODO: Подобрать более подходлящитее имя файлу
"""
from pymunk import Space

from Engine.EntityControllers import ManualController
from Engine.Scene.entities import Entity
from Engine.utils.utils import load_yaml


class BaseCharacter(Entity):
    """
    Базовый класс игрового персонажа
    На основе него делаются остальные классы
    """
    configs = load_yaml('src/configs/maincharacter.yaml')

    def __init__(self, physical_space: Space, x=0, y=0, brain=ManualController):
        super(BaseCharacter, self).__init__(physical_space, x, y,
                                            width=self.configs['width'], height=self.configs['height'],
                                            mass=self.configs['mass'], brain=brain)
        self.load_animations(self.configs['animations'])


def make_character(name, configs):
    """
    Создает класс сущности с нужными параметрами
    была претензия на метакласс, но он тут не особо нужен
    :param name: Имя сущности
    :param configs: конфигурация сущности
    :return:
    """
    return type(name, (BaseCharacter,), {'configs': configs})


# Главный герой
MainCharacter = make_character('MainCharacter', load_yaml('src/configs/maincharacter.yaml'))

# Главный антогонист - Данилио
Danilio = make_character('Danilio', load_yaml('src/configs/danilio.yaml'))

# Шестёрка Данилио
Udoser = make_character('Udoser', load_yaml('src/configs/udoser.yaml'))

# Шестёрка Данилио
Difurmen = make_character('Difurmen', load_yaml('src/configs/difurmen.yaml'))
