import json

import pygame
import yaml
from PIL import Image
from time import localtime, strftime


def get_time_for_save():
    """
    Возвращает строку с текущем именем
    :return: год_месяй_число_час_минуты_секунды
    """
    return strftime("%Y_%m_%d_%H_%M_%S", localtime())


def load_yaml(path):
    """
    Считываект yaml файл
    :param path: путь
    """
    with open(path, 'r') as file:
        return yaml.load(file, Loader=yaml.Loader)


def save_yaml(obj, path):
    """
    Записывает yaml файл
    :param obj: объект, который записываем в yaml
    :param path: путь
    :return: None
    """
    with open(path, 'w') as file:
        yaml.dump(obj, file, allow_unicode=True)


def load_json(path):
    """
    Считываект json файл
    :param path: путь
    """
    with open(path, 'r') as file:
        return json.load(file)


def save_json(obj, path, indent=2):
    """
    Записывает json файл
    :param indent: Если отступ является неотрицательным целым числом,
    то элементы массива JSON и члены объекта будут красиво напечатаны с этим уровнем отступа.
    Уровень отступа 0 будет вставлять только новые строки. Ни одно из них не является самым компактным представлением.
    :param obj: объект, который записываем в json
    :param path: путь
    :return: None
    """
    with open(path, 'w') as file:
        json.dump(obj, file, indent=indent)


def load_image(path):
    """
    Загружает картинку
    :param path: путь к картинке
    :return: None
    """
    return Image.open(path)


def pil_to_pygame(pil_image):
    """
    Преобразует изображение PIL в поверхность pygame
    :param pil_image: картинка PIL
    :return:
    """
    return pygame.image.fromstring(
        pil_image.tobytes(), pil_image.size, pil_image.mode).convert_alpha()
