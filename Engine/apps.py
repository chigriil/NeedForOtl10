import sys
from collections import deque
from math import pi, cos
from time import perf_counter
from typing import Union

import pygame
from pygame.draw import polygon

from settings import *


class MicroApp:
    """
    Базовый класс микро-прилдожения
    """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, lifetime: Union[int, float] = 0, FPS=60):
        # экран для отрисовки
        self.screen = screen

        # часы из модуля pygame
        self.clock = clock

        # FPS
        self.FPS = FPS

        # задания, выполняемые при выполнении условия
        # TODO: прикрутить нормальную обработку заданий
        self.tasks = []

        # Флаг, отвечающий за то, что приложение работает
        self.alive = True

        # Время жизни приложения
        self.lifetime = lifetime

        # Времена запуска и окончания приложения
        # Инициализируется при запуске
        self.start_time = None
        self.end_time = None

    def step(self, dt):
        """
        Двигает все во времени на dt
        :param dt: Квант времени
        """
        pass

    def draw(self):
        """
        Функция отрисовки экрана
        :return:
        """
        pass

    def run_once(self):
        """
        Запускается один раз в начале
        :return:
        """
        self.start_time = perf_counter()
        self.end_time = self.start_time + self.lifetime

    def run_tasks(self):
        """
        Задания для запуска на каждой итерации главного цикла
        TODO: Реализовать нормальную обработку
        :return:
        """
        for task in self.tasks:
            task()

    def atexit(self):
        """
        Действия при выходе из приложения
        :return: следущеее приложение, которое запустится сразу или None, если не предусмотрено следущее
        """
        return

    def on_iteration(self):
        """
        Функция, обрабатывающая одну итерацию приложения
        :return:
        """
        if perf_counter() > self.end_time:
            self.alive = False
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        self.run_tasks()
        self.step(self.clock.get_time() / 1000)
        self.draw()
        self.clock.tick(self.FPS)
        pygame.display.set_caption('{:.1f}'.format(self.clock.get_fps()))  # Вывод фпс в заголовок окна

    def run(self):
        """
        Запуск главного цикла
        :return: результат выполнения self.atexit()
        """
        self.run_once()
        while self.alive:
            self.on_iteration()
        return self.atexit()


class App:
    """
    Класс приложения, исполнябющий в себе микро-приложения
    """

    def __init__(self, micro_apps: list[MicroApp] = None):
        """
        :param micro_apps: список приложений в порядке очереди
        """
        # Не стоит использовать изменяемы параметры в качестве значений по умолчанию
        if micro_apps is None:
            micro_apps = []
        self.micro_apps = deque(micro_apps)

    def run(self):
        """
        Главный цикл приложения, перебирающий микро-приложения
        :return:
        """
        # Крутимся, пока есть приложения в очереди
        running = True

        # Текущее приложение
        app = None

        while running:

            try:
                # Вынимаем приложение из очереди, если app это None
                if app is None:
                    app = self.micro_apps.popleft()

                # Получаем слудущее приложение или None
                app = app.run()

            except IndexError:
                # Вызывается, если акончились приложения в очереди, ставим флаг running = False
                running = False

            except Exception as e:
                # Псевдо-обработка других исключений
                raise e


class Init(MicroApp):
    """
    Приложение инициализации
    проверяет работоспособность кода
    # TODO: запускает юниттесты
    """

    def __init__(self, screen, clock):
        super(Init, self).__init__(screen, clock)
        self.start_tests()

    @staticmethod
    def start_tests():
        """
        Проверка версии питона
        Если < 3.9.0 Выбрасываем исключение
        Python 3.9.0 нужно, чтобы было меньше импортов из модуля typing
        В следущих версиях игры, чтобы проще обновлять self.__dict__ у классов
        Лень запариваться с нормальной сериализацией
        :return:
        """
        if sys.hexversion < 0x30900f0:
            raise SystemError("Даня, я знаю это ты. Установи питон 3.9.0 или выше")


class LoadingScreen(MicroApp):
    """
    Приложение загрузочного экрана
    """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, lifetime=6):
        super(LoadingScreen, self).__init__(screen, clock)
        self.end_time = perf_counter() + lifetime
        # Фоновый цвет
        self.background_color = (100, 100, 254)
        # Цвета, которыми будут переливаться буквы
        self.colors = [(212, 6, 6), (238, 156, 0), (227, 255, 0), (6, 191, 0), (0, 26, 152)]

        # Музыка на загрузочном экране
        self.bgmusic = pygame.mixer.Sound('Resources/Music/lodingscreen.ogg')

        # Цыганская магия, которая рисует черный прямоугольник с вырезанными прозраычными буквами
        # Точнее создает трафарет
        # Лучше не вникать (реально)
        # Инициализация шрифта
        self.font = pygame.font.SysFont('maturascriptcapitals', SCREEN_HEIGHT // 5)
        # Рисование просто букв цвета temp_color на поверхности
        temp_color = (0, 0, 255)
        self.temp = self.font.render('Need For Otl 10', False, temp_color)
        # Центрирование поверхности на экране
        self.rect = self.temp.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        # Сама поверхность для трафорента текста
        self.text_surface = pygame.Surface(self.rect.size).convert_alpha()
        # Заливаем её цветом, который будем превращать в прозрачный
        self.text_surface.fill((1, 1, 1))
        # Рисуем текст на ней
        self.text_surface.blit(self.temp, (0, 0))
        # Меняем temp_color на прозрачную зону
        self.text_surface.set_colorkey(temp_color)

        # Поверхность на которой будет рисоваться анимированные буквы
        # Потом ее рисуем на экране
        # Нужно, чтобы можно было легко реализовать цыганскую магию
        self.camera_surface = pygame.Surface(self.rect.size).convert_alpha()

        # Технические перемнные
        # Сдвиг переливов (мб при больших значениях упадет точность, но это займет много времени)
        self.position = 0
        # Скорость движения полос
        self.speed = 70
        # Высота полос (она же высота текста)
        self.height_of_strip = self.text_surface.get_height()
        # Кол-во полос на тексте (должно быть кратно кол-ву цветов в self.colors, иначе не будет циклического перехода)
        self.num_strips = 5 * len(self.colors)
        # Длина полос (тоже вычисляется через цыганскую магию)
        # Лучше не трогать
        self.len_of_strip = (self.camera_surface.get_width() + self.height_of_strip * cos(pi / 4)) / (
                    self.num_strips - 1)

    def run_once(self):
        self.bgmusic.play()

    def prepare_text(self):
        """
        Рисует буквы с переливающимся цветом
        :return:
        """

        # Рисуем полоски (параллелограммы)
        for strip in range(self.num_strips):
            x_coord = (strip * self.len_of_strip + self.position) % (
                        self.len_of_strip * self.num_strips) - self.len_of_strip
            coords = (
                (x_coord, 0),
                (x_coord - self.height_of_strip * cos(pi / 4), self.height_of_strip),
                (x_coord + self.len_of_strip - self.height_of_strip * cos(pi / 4), self.height_of_strip),
                (x_coord + self.len_of_strip, 0)
            )
            polygon(self.camera_surface, self.colors[strip % len(self.colors)], coords)

        # Вырезаем буквы
        self.camera_surface.blit(self.text_surface, (0, 0))

        # Делаем прозрачным то, что нужно
        # удалив это строчку, можно накинуть 20 фпс
        self.camera_surface.set_colorkey((1, 1, 1))

    def atexit(self):
        """
        Тормозим фоновую музыку
        :return: None
        """
        self.bgmusic.stop()

    def step(self, dt):
        """
        Двигаем полоски
        :param dt: квант времени
        :return:
        """
        self.position += self.speed * dt

    def draw(self):
        """
        Рисуем всё на экране
        :return:
        """
        self.screen.fill(self.background_color)
        self.prepare_text()
        self.screen.blit(self.camera_surface, self.rect.topleft)

        pygame.display.update()
