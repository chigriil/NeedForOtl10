from math import degrees

import pygame
import pymunk
from pymunk import Vec2d, Space

from Engine.utils.physical_primitives import PhysicalRect, BoundingBox

ObjectRegistry = {}


class GameObject:
    """
    Базовый класс игровго объекта
    """

    def __init__(self, x, y, width=0.3, height=0.3, sprite=None):
        """

        :param x: x координата левого нижнего угла объекта
        :param y: y координата левого нижнего угла объекта
        :param width: ширина описанного прямоугольника объекта
        :param height: высота описанного прямоугольника объекта
        :param sprite: спрайт объекта
        """
        self._position = Vec2d(x, y)
        self.width = width
        self.height = height
        self.sprite = sprite
        if self.sprite is not None:
            # Переворачиваем спрайт
            self.sprite = pygame.transform.flip(self.sprite, False, True).convert_alpha()

        self.body_rect = PhysicalRect(x, y, width, height)

        # Преобразованное изображения спрайта
        # Имеет размер, как проекция объекта на поверхность камеры
        # Нужно для оптимизации
        self.scaled_image = self.sprite
        self.last_camera_distance = -1  # Дистанция от камеры да сцены

    def __repr__(self):
        return self.__class__.__name__

    def step(self, dt):
        """
        Эволюция системы во времени
        Предполагается, что метод будет использоваться для обработки анимации
        Не обрабатывает физику, этим занимается pymunk
        :param dt: квант времени
        :return:
        """
        self.body_rect.bottomleft = self._position

    def __view__(self, camera):
        """
        Рисует объект на поверхности камеры
        :param camera: сама камера
        :return:
        """

        # Проекция описанного прямоугольника на камеру
        rect_for_camera: pygame.Rect = camera.projection_of_rect(self.body_rect)

        # Если не пересекается с экраном, то не рисуем
        if not rect_for_camera.colliderect(camera.screen.get_rect()):
            return

        # Рисование спрайта
        # Рисуем серый прямоугольник и прекращаем рисование, если нет спрайта
        if self.sprite is None:
            camera.project_rect(self.body_rect, (100, 100, 100))
            return

        # Если преобразованный спрайт считался для другой дистанции от камеры до сцены
        # То пересчитываем его
        if self.last_camera_distance != camera.distance:
            self.scaled_sprite = pygame.transform.scale(self.sprite, rect_for_camera.size)
            self.last_camera_distance = camera.distance

        # Рисуем спрайт игрока
        camera.temp_surface.blit(self.scaled_sprite, rect_for_camera)

    def __devview__(self, camera):
        """
        Отображение технической информации
        Например описанного прямоугольника и точки с координатами объекта, центра масс
        :param camera: камера
        :return:
        """
        camera.dev_rect(self.body_rect, (255, 0, 0), 5)
        camera.project_point(self.body_rect.bottomleft, 7)  # позиция объекта
        camera.project_point(self.body_rect.centre, 7, (255, 255, 0))  # центр масс объекта

    @property
    def position(self):
        return self._position

    def __init_subclass__(cls, **kwargs):
        ObjectRegistry[cls.__name__] = cls


class PhysicalGameObject(GameObject):
    """
    Базовый класс физического игрового объекта
    """

    def __init__(self, x, y, width=1, height=1, sprite=None, lifetime=1,
                 scene=None, body: pymunk.Body = None, shape: pymunk.Shape = None,
                 angle=0, mass=1, moment=None, elasticity=0, friction=0.6, type_=pymunk.Body.STATIC,
                 damage=None, owner=None, if_damaged='none', if_damaged_many='disappear'):
        """
        Если вы хотите установить свою фарму объекта, то при наследовании перед вызовом super().__init__
        нужно определить body и shape, чтобы всё корректно работало.
        Это нужно сделать, т.к. выяснилось, что в конструктор класса Circle обязательно надо передать body, т.к.
        c None, он отказывается работать
        пример кода можно посмотреть в классе DynamicCircularObject

        Небольшое пояснение, у объекта есть два описанных прямоугольника
        1) Начальный self.body_rect, на него натягиваются спрайты
        2) Временной self.bounding, его стороны параллельны осям координат, пока нужен только для девмода

        Если спрайт не указан, то будет рисоваться серый прямоугольник
        Если форма не указана, то будет использоваться прямоугольник с шириной = width и высотой = height
        Если момент инерции не указан, то будет расчитан для прямоугольника, описанного выше
        elasticity и friction используются для внутренних нужд pymunk

        Типы DYNAMIC, KINEMATIC, STATIC
        DYNAMIC - полноценных физический объект
        KINEMATIC - не реагирует на столкновения и гравитацию, перемещаются вручную
        STATIC - статичный объект, не может передвигаться, из-за этого даёт сильный прирост в производительности
        :param x: x координата левого нижнего угла объекта
        :param y: y координата левого нижнего угла объекта
        :param width: ширина описанного прямоугольника объекта
        :param height: высота описанного прямоугольника объекта
        :param sprite: спрайт объекта
        :param lifetime: время жизни объекта
        :param scene: игровая сцена
        :param shape: физическая форма тела
        :param angle: начальный угол поворота тела против часовой (в радианах)
        :param mass: масса объекта
        :param moment: момент инерции
        :param elasticity: эластичность
        :param friction: коэффициент трения
        :param type_: тип объекта (DYNAMIC, KINEMATIC, STATIC)
        :param damage: урон при попадании в сущность, не являющейся владельцем, мб None
        :param owner: владелеец (точнее id), мб None
        :param if_damaged: действие после нанесения урона 1 раз
        :param if_damaged_many: действие после нанесения урона на 1 итерации цикла проверки урона
        """
        super(PhysicalGameObject, self).__init__(x, y, width, height, sprite=sprite)
        if isinstance(scene, Space):
            raise
        if scene is None:
            raise AttributeError("Нужно задать обязательно сцену")

        # Игровая сцена, на которой находится объект
        self.scene = scene

        # Оставшееся время жизни объекта
        self.lifetime = lifetime

        # Владелец
        self.owner = owner

        # Урон
        self.damage = damage
        self.if_damaged = if_damaged
        self.if_damaged_many = if_damaged_many
        # Подробнее про состояния можно почитать в self._damaged

        # Цыганская магия
        self.physical_space = scene.physical_space

        # Если момент не задан, то считаем его для прямоугольника
        if moment is None:
            moment = pymunk.moment_for_box(mass, (self.width, self.height))

        if body is None:
            body = pymunk.Body(mass, moment, type_)

        body.angle = angle
        body.position = x + width / 2, y + height / 2

        self.body = body

        # Если форма не задана, то используем прямоугольник
        if shape is None:
            shape = pymunk.Poly.create_box(self.body, self.body_rect.size)

        self.body_shape = shape
        self.body_shape.elasticity = elasticity
        self.body_shape.friction = friction

        self.physical_space.add(self.body, self.body_shape)

    def step(self, dt):
        # пересчитываем позицию описанного прямоугольника
        self.body_rect.centre = self.body.position

        # уменьшаем оставшееся время жизни
        self.lifetime -= dt

    def kill(self):
        """
        Удаляет объект из физического пространства
        :return:
        """
        self.physical_space.remove(self.body)
        self.physical_space.remove(self.body_shape)

    def _damaged(self, action):
        # Ничего не делать при none
        if action == 'none':
            return

        # Пропасть
        elif action == 'disappear':
            self.lifetime = -1

        # Потерять урон
        elif action == 'lose_damage':
            self.damage = None

        # устанавливает новое время жизни
        # формат действия 'new_lifetime_{time}'
        # time - новое время жизни
        elif action.startswith('new_lifetime'):
            self.lifetime = float(action.split('_')[-1])

    def damaged(self):
        """
        действие при нанесении урона персонажу 1 раз
        :return:
        """
        self._damaged(self.if_damaged)

    def damaged_many(self):
        """
        действие при нанесении урона после 1 цикла проверки урона
        :return:
        """
        self._damaged(self.if_damaged_many)

    def no_sprite_view(self, camera):
        """
        Рисует образ объекта, если нет спрайта
        :param camera: камера
        :return:
        """
        camera.project_poly(self.boundingbox, (100, 100, 100))

    def __view__(self, camera):
        """
        Рисует объект на поверхности камеры
        :param camera: сама камера
        :return:
        """

        # Проекция описанного прямоугольника на камеру
        rect_for_camera: pygame.Rect = camera.projection_of_rect(self.boundingbox2)

        # Если не пересекается с экраном, то не рисуем
        if not rect_for_camera.colliderect(camera.screen.get_rect()):
            return

        # Рисование спрайта
        # Рисуем серый прямоугольник и прекращаем рисование, если нет спрайта
        if self.sprite is None:
            self.no_sprite_view(camera)
            return

        # Если преобразованный спрайт считался для другой дистанции от камеры до сцены
        # То пересчитываем его
        if self.last_camera_distance != camera.distance:
            self.scaled_sprite = pygame.transform.scale(self.sprite, camera.projection_of_rect(self.body_rect).size)
            self.last_camera_distance = camera.distance

        # Рисуем спрайт игрока
        # Поварачиваем
        prepared_sprite = pygame.transform.rotate(self.scaled_sprite, -degrees(self.body.angle))
        # Рисуем
        camera.temp_surface.blit(prepared_sprite, prepared_sprite.get_rect(center=rect_for_camera.center).topleft)

    def __devview__(self, camera):
        """
        Отображение технической информации
        Например описанного прямоугольника и точки с координатами объекта
        :param camera: камера
        :return:
        """
        bb = self.body_shape.bb
        camera.project_poly(self.boundingbox, (108, 70, 117), 5)  # описанный прямоугольник 2 типа(см. init)
        camera.dev_rect(BoundingBox(bb), (255, 0, 0), 3)  # описанный прямоугольник 1 типа(см. init)
        camera.project_point((bb.left, bb.bottom), 7)  # позиция объекта
        camera.project_point(self.body.center_of_gravity + self.body.position, 7, (255, 255, 0))  # центр масс

    @property
    def boundingbox2(self) -> BoundingBox:
        """
        :return: описанный прямоугольник, стороны которого праллельны осям координат
        """
        return BoundingBox(self.body_shape.bb)

    @property
    def boundingbox(self) -> list[Vec2d]:
        """
        :return: описанный прямоугольник, на который натягивается спрайт
        """
        return self.body_rect.get_rotated(self.body.angle)

    @property
    def position(self):
        return self.body.position - Vec2d(self.width / 2, self.height / 2)

    def save_data(self):
        """
        Выдаёт данные для сериализации.
        Обязательно перегрузить при наследоывании
        :return:
        """
        return self


class StaticRectangularObject(PhysicalGameObject):
    def __init__(self, x, y, width=0.3, height=0.3, sprite=None,
                 scene=None, angle=0, mass=1, moment=None, elasticity=0, friction=0.6):
        super(StaticRectangularObject, self).__init__(x=x, y=y, width=width, height=height,
                                                      sprite=sprite, scene=scene, angle=angle,
                                                      mass=mass, moment=moment, elasticity=elasticity,
                                                      friction=friction, type_=pymunk.Body.STATIC)


class DynamicRectangularObject(PhysicalGameObject):
    def __init__(self, x, y, width=0.3, height=0.3, sprite=None,
                 scene=None, angle=0, mass=1, moment=None, elasticity=0, friction=0.6):
        super(DynamicRectangularObject, self).__init__(x=x, y=y, width=width, height=height, sprite=sprite,
                                                       scene=scene, angle=angle,
                                                       mass=mass, moment=moment, elasticity=elasticity,
                                                       friction=friction, type_=pymunk.Body.DYNAMIC)


class DynamicCircularObject(PhysicalGameObject):
    def __init__(self, x, y, radius=0.3, sprite=None,
                 scene=None, angle=0, mass=1, moment=None, elasticity=0, friction=0.6):
        if moment is None:
            moment = pymunk.moment_for_box(mass, (radius, radius))

        body = pymunk.Body(mass, moment)
        shape = pymunk.Circle(body, radius=radius)

        super(DynamicCircularObject, self).__init__(x=x, y=y, width=radius, height=radius,
                                                    scene=scene, sprite=sprite,
                                                    body=body, shape=shape,
                                                    angle=angle, mass=mass, moment=moment, elasticity=elasticity,
                                                    friction=friction, type_=pymunk.Body.DYNAMIC)

        self.body_rect = PhysicalRect(x - radius / 2, y - radius / 2, 2 * radius, 2 * radius)

    def no_sprite_view(self, camera):
        camera.project_circle(self.boundingbox2.centre, self.body_shape.radius, (100, 100, 100))
