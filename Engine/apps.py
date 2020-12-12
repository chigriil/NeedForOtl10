import sys
from collections import deque
from time import perf_counter
from typing import Union

import pygame


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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.atexit()
                pygame.quit()
                sys.exit()

    def on_iteration(self):
        """
        Функция, обрабатывающая одну итерацию приложения
        :return:
        """
        if perf_counter() > self.end_time:
            self.alive = False
            return
        self.handle_events()
        self.run_tasks()
        self.step(self.clock.get_time() / 1000)
        self.draw()
        self.clock.tick(self.FPS)

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
                    if len(self.micro_apps) == 0:
                        break
                    app = self.micro_apps.popleft()

                # Получаем слудущее приложение или None
                app = app.run()

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
