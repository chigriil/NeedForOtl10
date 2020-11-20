"""
Модуль с разными исключениями
"""

from random import choice

phrases = ["Ты как это вообще сделал?",
           "Ты первый кто смог это сломать",
           "Я тебе просто похлопаю",
           "Лучший прогер на земле. Теперь чини",
           "Пора тебя уволить"]


class YouAreTeapot(Exception):
    """
    Исключения, высмеивающее програмиста
    """

    def __init__(self, text):
        super(YouAreTeapot, self).__init__(text)
        print(choice(phrases))
        self.txt = text
