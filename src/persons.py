"""
Тут храняться классы игрока и антогонистов
TODO: Подобрать более подходлящитее имя файлу
"""
import os

from Engine.Scene.entities import BaseCharacter
from Engine.utils.utils import load_yaml
from settings import person_configs_path


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


def load_characters():
    """
    Загрузка персонажей
    """
    for person_config_file in os.listdir(person_configs_path):

        if not person_config_file.endswith('.yaml') or person_config_file.startswith('_'):
            continue

        config = load_yaml(os.path.join(person_configs_path, person_config_file))

        make_character(config)
