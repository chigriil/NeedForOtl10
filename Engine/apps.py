import sys
from collections import deque
from math import pi, cos
from time import perf_counter
from typing import Union

import pygame
from pygame.draw import polygon

from settings import *


class MicroApp:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, lifetime: Union[int, float] = 0):
        self.screen = screen
        self.clock = clock
        self.tasks = []
        self.alive = True
        self.lifetime = lifetime
        self.starttime = None
        self.endtime = None

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
        self.starttime = perf_counter()
        self.endtime = self.starttime + self.lifetime

    def run_tasks(self):
        """
        Задания для запуска на каждой итерации главного цикла
        :return:
        """
        for task in self.tasks:
            task()

    def atexit(self):
        return

    def on_iteration(self):
        if perf_counter() > self.endtime:
            self.alive = False
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        self.run_tasks()
        self.step(self.clock.get_time() / 1000)
        self.draw()
        self.clock.tick()
        pygame.display.set_caption('{:.1f}'.format(self.clock.get_fps()))  # Вывод фпс в заголовок окна

    def run(self):
        """
        Запуск главного цикла
        :return:
        """
        self.run_once()
        while self.alive:
            self.on_iteration()
        self.atexit()


class App:
    def __init__(self, microapps=None, currentapp: MicroApp = None):
        if microapps is None:
            microapps = []
        self.currenapp = currentapp
        self.microapps = deque(microapps)

    def run(self):
        running = True
        nextapp = None
        while running:
            try:
                if nextapp is None:
                    nextapp = self.microapps.popleft()
                nextapp = nextapp.run()

            except IndexError:
                running = False

            except Exception as e:
                raise e


class Init(MicroApp):
    def __init__(self, screen, clock):
        super(Init, self).__init__(screen, clock)
        self.start_tests()

    @staticmethod
    def start_tests():
        if sys.hexversion < 0x30900f0:
            raise SystemError("Даня, я знаю это ты. Установи питон 3.9.0 или выше")


class LoadingScreen(MicroApp):
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, lifetime=6):
        super(LoadingScreen, self).__init__(screen, clock)
        self.endtime = perf_counter() + lifetime
        # Фоновый цвет
        self.BGCOLOR = (100, 100, 254)
        # Цвета, которыми будут переливаться буквы
        self.colors = [(212, 6, 6), (238, 156, 0), (227, 255, 0), (6, 191, 0), (0, 26, 152)]

        # Музыка на загрузочном экране
        self.bgmusic = pygame.mixer.Sound('Resources/Music/lodingscreen.ogg')

        # Цыганская магия, которая рисует черный прямоугольник с вырезанными прозраычными буквами
        # Точнее создает трафарет
        # Лучше не вникать (реально)
        # Инициализация шрифта
        self.font = pygame.font.SysFont('maturascriptcapitals', SCREEN_HEIGHT // 5)
        # Рисование просто букв цвета tempcolor на поверхности
        tempcolor = (0, 0, 255)
        # self.temp = self.font.render('Physt Fighter', False, tempcolor)
        self.temp = self.font.render('Need For Otl 10', False, tempcolor)
        # Центрирование поверхности на экране
        self.rect = self.temp.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        # Сама поверхность для трафорента текста
        self.textsurface = pygame.Surface(self.rect.size).convert_alpha()
        # Заливаем её цветом, который будем превращать в прозрачный
        self.textsurface.fill((1, 1, 1))
        # Рисуем текст на ней
        self.textsurface.blit(self.temp, (0, 0))
        # Меняем tempcolor на прозрачную зону
        self.textsurface.set_colorkey(tempcolor)

        # Поверхность на которой будет рисоваться анимированные буквы
        # Потом ее рисуем на экране
        # Нужно, чтобы можно было легко реализовать цыганскую магию
        self.tempsurface = pygame.Surface(self.rect.size).convert_alpha()

        # Технические перемнные
        # Сдвиг переливов (мб при больших значениях упадет точность, но это займет много времени)
        self.position = 0
        # Скорость движения полос
        self.speed = 70
        # Высота полос (она же высота текста)
        self.heightpolos = self.textsurface.get_height()
        # Кол-во полос на тексте (должно быть кратно кол-ву цветов в self.colors, иначе не будет циклического перехода)
        self.numpolos = 5 * len(self.colors)
        # Длина полос (тоже вычисляется через цыганскую магию)
        # Лучше не трогать
        self.lenpolos = (self.tempsurface.get_width() + self.heightpolos * cos(pi / 4)) / (self.numpolos - 1)

    def run_once(self):
        self.bgmusic.play()

    def prepare_text(self):
        """
        Рисует буквы с переливающимся цветом
        :return:
        """
        for polosa in range(self.numpolos):
            x_coord = (polosa * self.lenpolos + self.position) % (self.lenpolos * self.numpolos) - self.lenpolos
            coords = (
                (x_coord, 0),
                (x_coord - self.heightpolos * cos(pi / 4), self.heightpolos),
                (x_coord + self.lenpolos - self.heightpolos * cos(pi / 4), self.heightpolos),
                (x_coord + self.lenpolos, 0)
            )
            polygon(self.tempsurface, self.colors[polosa % len(self.colors)], coords)
        self.tempsurface.blit(self.textsurface, (0, 0))
        self.tempsurface.set_colorkey((1, 1, 1))  # удалив это строчку, можно накинуть 20 фпс

    def atexit(self):
        self.bgmusic.stop()

    def step(self, dt):
        self.position += self.speed * dt

    def draw(self):
        self.screen.fill(self.BGCOLOR)
        self.prepare_text()
        self.screen.blit(self.tempsurface, self.rect.topleft)

        pygame.display.update()
