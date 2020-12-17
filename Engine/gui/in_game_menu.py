import pygame
import sys

from Engine.apps import MicroApp


class InGameMenu(MicroApp):
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        super(InGameMenu, self).__init__(screen, clock)
        self.FPS = 10
        # Фоновый цвет
        self.background_color = (255, 100, 100)
        # Шрифт
        self.font = pygame.font.SysFont('Ariel', self.screen.get_height() // 24)
        self.title_font = pygame.font.SysFont('Ariel', self.screen.get_height() // 8)
        # Цвет шрифта
        self.font_color = (0, 0, 0)
        # Поверхности с текстом
        self.text_surface_1 = self.title_font.render('PAUSE', True, self.font_color)
        self.text_surface_2 = self.font.render('Сохранить игру', True, self.font_color)
        self.text_surface_2_rect = pygame.Rect(self.screen.get_width() // 2 - self.text_surface_2.get_width() // 2,
                                               self.screen.get_height() * 10 // 24,
                                               self.text_surface_2.get_width(),
                                               self.text_surface_2.get_height())
        self.text_surface_3 = self.font.render('Вернуться в игру', True, self.font_color)
        self.text_surface_3_rect = pygame.Rect(self.screen.get_width() // 2 - self.text_surface_3.get_width() // 2,
                                               self.screen.get_height() * 14 // 24,
                                               self.text_surface_3.get_width(),
                                               self.text_surface_3.get_height())
        # self.text_surface_4 = self.font.render('Выход к главному меню', True, self.font_color)
        self.text_surface_5 = self.font.render('Выход из игры', True, self.font_color)
        self.text_surface_5_rect = pygame.Rect(self.screen.get_width() // 2 - self.text_surface_5.get_width() // 2,
                                               self.screen.get_height() * 16 // 24,
                                               self.text_surface_5.get_width(),
                                               self.text_surface_5.get_height())

    def draw(self):
        pygame.draw.rect(self.screen, self.background_color, pygame.Rect(self.screen.get_width() // 4,
                                                                         self.screen.get_height() // 4,
                                                                         self.screen.get_width() // 2,
                                                                         self.screen.get_height() // 2))

        self.screen.blit(self.text_surface_1, (self.screen.get_width() // 2 - self.text_surface_1.get_width() // 2,
                                               self.screen.get_height() * 6 // 24))
        self.screen.blit(self.text_surface_2, (self.screen.get_width() // 2 - self.text_surface_2.get_width() // 2,
                                               self.screen.get_height() * 10 // 24))
        self.screen.blit(self.text_surface_3, (self.screen.get_width() // 2 - self.text_surface_3.get_width() // 2,
                                               self.screen.get_height() * 13 // 24))
        # self.screen.blit(self.text_surface_4, (self.screen.get_width() // 2 - self.text_surface_4.get_width() // 2,
                                               # self.screen.get_height() * 14 // 24))
        self.screen.blit(self.text_surface_5, (self.screen.get_width() // 2 - self.text_surface_5.get_width() // 2,
                                               self.screen.get_height() * 16 // 24))

    def on_iteration(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.atexit()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Выход из игры
                if self.text_surface_5_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                # Сохранение игры
                if self.text_surface_2_rect.collidepoint(event.pos):
                    pass
                # Возвращение в игру
                if self.text_surface_3_rect.collidepoint(event.pos):
                    self.alive = False
        self.draw()
        self.clock.tick(self.FPS)
        pygame.display.flip()

