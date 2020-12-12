"""
Тёмный лес без документации, не стоит сюда лезть. Или хотябы подождите документации.
Основная суть модуля - залезть очень глубоко в питон и сделать что-то магическое
"""
import importlib
import importlib.util
import json
import os
import sys
from types import ModuleType

import yaml

# Регистр загрузчиков
ex_registry = []


class ExDataLoader(importlib.abc.Loader):
    """
    Базовый класс загрузчика файлов с расширениями != .py, как модулей питона
    """
    # Расширение файла
    ext = '.none'

    @staticmethod
    def repack(module, data):
        """
        Выполняет запись данных в модуль
        :param module:
        :param data:
        :return:
        """
        if isinstance(data, dict):
            for key, value in data.items():
                # Выкидываем все названия, начинающиеся и заканчивающиеся на '__',
                # чтобы случайно не перегрузить магические методы
                if key.startswith('__') and key.endswith('__') or hasattr(module, key):
                    continue
                setattr(module, key, value)
        # module.raw_data = data

    def exec_module(self, module: ModuleType) -> None:
        """
        Выполняет загрузку модуля
        :param module: модуль
        :return:
        """
        with open(module.__spec__.origin, 'r') as file:
            # print(f'Loading {module.__spec__.origin}')
            data = self.load_data(file)
            self.repack(module, data)

    @staticmethod
    def load_data(data):
        """
        Загружает данные из прочитанного содержимого файла
        :param data:
        :return:
        """
        return None

    def __init_subclass__(cls):
        """
        При иницализации наследника, автоматически добавляет его в регистр загрузчиков
        :return:
        """
        ex_registry.append(cls)

        # Если у субкласса не поля ext, то считаем,
        # что он загружает файлы с расширение = названию класса нижним регистром
        if not hasattr(cls, 'ext'):
            setattr(cls, 'ext', '.' + cls.__name__.lower())


class JSON(ExDataLoader):
    """
    Загрузчик json, как модуля питона
    """
    ext = '.json'

    @staticmethod
    def load_data(data):
        return json.load(data)


class YAML(ExDataLoader):
    """
    Загрузчик yaml, как модуля питона
    """
    ext = '.yaml'

    @staticmethod
    def load_data(data):
        return yaml.load(data, Loader=yaml.SafeLoader)


class ExPathFinder(importlib.abc.MetaPathFinder):
    """
    Кастомный импортёр файлов, как модулей питона
    """

    def find_spec(self, fullname, path, target=...):
        # Если не указан путь, считаем, что ищем в директории основногно файла программы
        if not path:
            path = [os.getcwd()]

        # Если импортируем из пакета
        if '.' in fullname:
            fullname = fullname.split('.')[-1]

        # Ищем подходящий файл для импорта
        for cat in path:
            # Пытаемся импортить  с помощью кастомных загрузчиков модулей
            for loader in ex_registry:
                # Полный путь до файла
                in_path = os.path.join(cat, fullname) + loader.ext

                # Если файл существует, то импортим
                if os.path.exists(in_path):
                    return importlib.util.spec_from_file_location(
                        name=fullname + loader.ext,
                        location=in_path,
                        loader=loader()
                    )


def init():
    # Добавляем кастомнеый импортёр в meta_path
    sys.meta_path.append(ExPathFinder())
    print('Dark magic activated')
