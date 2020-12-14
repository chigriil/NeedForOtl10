"""
Класс содержащий геометрическое примитивы из физической реализации сцены
"""
from pygame import Rect
from pymunk import Vec2d, BB


class PhysicalRect:
    """
    Прямоугольник
    """

    def __init__(self, x, y, width, height):
        """
        :param x: координата x левого нижнего края прямоугольника
        :param y: координата y левого нижнего края прямоугольника
        :param width: ширина прямоугольника
        :param height: высота прямоугольника
        """
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height

    @property
    def centre(self) -> Vec2d:
        return Vec2d(self.__x + self.__width / 2,
                     self.__y + self.__height / 2)

    @centre.setter
    def centre(self, newcentre):
        self.__x, self.__y = newcentre - (self.__width / 2, self.__height / 2)

    @property
    def bottomleft(self) -> Vec2d:
        """
        Возвращает координаты левого нижнего угла прямоугольника
        :return: координаты левого нижнего угла прямоугольника
        """
        return Vec2d(self.x, self.y)

    @bottomleft.setter
    def bottomleft(self, newbottomleft):
        """
        Устанавлявает координаты левого нижнего угла прямоугольника
        :param newbottomleft: новые координаты левого нижнего угла прямоугольника
        """
        self.__x, self.__y = newbottomleft

    @property
    def topleft(self) -> Vec2d:
        """
        Возвращает координаты левого верхнего угла прямоугольника
        :return: координаты левого верхнего угла прямоугольника
        """
        return Vec2d(self.x, self.y + self.__height)

    @property
    def bottomright(self) -> Vec2d:
        """
        Возвращает координаты правого нижнего нижнего угла прямоугольника
        :return: координаты правого нижнего угла прямоугольника
        """
        return Vec2d(self.x + self.__width, self.y)

    @property
    def topright(self) -> Vec2d:
        """
        Возвращает координаты правого нижнего верхнего угла прямоугольника
        :return: координаты правого верхнего угла прямоугольника
        """
        return Vec2d(self.x + self.__width,
                     self.y + self.__height)

    @property
    def left(self):
        """
        Возвращает координату x левой границы
        :return:
        """
        return self.__x

    @property
    def right(self):
        """
        Возвращает координату x правой границы
        :return:
        """
        return self.__x + self.__width

    @property
    def bottom(self):
        """
        Возвращает координату y нижней границы
        :return:
        """
        return self.__y

    @property
    def top(self):
        """
        Возвращает координату y верхней границы
        :return:
        """
        return self.__y + self.__height

    @property
    def width(self):
        """
        Возвращает ширину прямоугольника
        :return: ширина прямоугольника
        """
        return self.__width

    @property
    def height(self):
        """
        Возвращает высоту прямоугольника
        :return: высоту прямоугольника
        """
        return self.__height

    @property
    def size(self):
        """
        Возвращает размеры прямоугольника
        :return: кортеж (ширина, высота)
        """
        return self.__width, self.__height

    @property
    def x(self):
        """
        :return: координата x левого нижнего края прямоугольника
        """
        return self.__x

    @property
    def y(self):
        """
        :return: координата н левого нижнего края прямоугольника
        """
        return self.__y

    def vertices(self):
        return [
            self.topleft,
            self.topright,
            self.bottomright,
            self.bottomleft
        ]

    def get_rotated(self, angle) -> list[Vec2d]:
        return [(vertex - self.centre).rotated(angle) + self.centre
                for vertex in self.vertices()]

    def point_in_rect(self, point):
        """
        Проверяет, находится ли точка внутри прямоугольника
        :param point: координаты точки
        :return:
        """
        return self.__x <= point.x <= self.__x + self.__width and self.__y <= point.y <= self.__y + self.__height

    def check_intersection(self, rect: 'PhysicalRect'):
        """
        Проверяет, пересекаются ли прямоугольники
        :param rect: другой прямоугольник
        :return:
        """
        # Поочерёдная проверка попадания вершины прямоугольника rect внуть self
        return \
            self.__x <= rect.__x <= self.__x + self.__width and \
            self.__y <= rect.__y <= self.__y + self.__height or \
            self.__x <= rect.__x <= self.__x + self.__width and \
            self.__y <= rect.__y + rect.__height <= self.__y + self.__height or \
            self.__x <= rect.__x + rect.__width <= self.__x + self.__width and \
            self.__y <= rect.__y + rect.__height <= self.__y + self.__height or \
            self.__x <= rect.__x + rect.__width <= self.__x + self.__width and \
            self.__y <= rect.__y <= self.__y + self.__height

    def check_overlap(self, rect: 'PhysicalRect'):
        """
        Проверяет, перекрывает ли self прямоугольник rect полностью
        :param rect: другой прямоугольник
        :return:
        """
        # Поочерёдная проверка попадания вершины прямоугольника rect внуть self
        return \
            self.__x <= rect.__x <= self.__x + self.__width and \
            self.__y <= rect.__y <= self.__y + self.__height and \
            self.__x <= rect.__x <= self.__x + self.__width and \
            self.__y <= rect.__y + rect.__height <= self.__y + self.__height and \
            self.__x <= rect.__x + rect.__width <= self.__x + self.__width and \
            self.__y <= rect.__y + rect.__height <= self.__y + self.__height and \
            self.__x <= rect.__x + rect.__width <= self.__x + self.__width and \
            self.__y <= rect.__y <= self.__y + self.__height

    def to_pygame_rect(self):
        """
        Делает из этого прямоугольника прямогуольник pygame
        :return:
        """
        return Rect(self.__x, self.__y, self.__width, self.__height)

    def save_data(self):
        """
        Возвращает данные для сериализации
        :return:
        """
        return {
            'x': self.x,
            'y': self.y,
            'width': self.__width,
            'height': self.__height
        }

    def __imul__(self, other):
        """
        Маштабирует длины сторон
        :param other: есои other это скаляр, то умножает длину и ширину на него,
        если нет, то перемножает покомпонентно
        :return:
        """
        if hasattr(other, '__getitem__'):
            self.__width *= other[0]
            self.__height *= other[1]
        else:
            self.__width *= other
            self.__height *= other

    def __mul__(self, other):
        """
        Возвращает прямоугольник с маштабированными длинами сторон
        :param other: есои other это скаляр, то умножает длину и ширину на него,
        если нет, то перемножает покомпонентно
        :return:
        """
        w, h = self.__width, self.__height
        if hasattr(other, '__getitem__'):
            w *= other[0]
            h *= other[1]
        else:
            w *= other
            h *= other

        return PhysicalRect(self.__x, self.__y, w, h)


class BoundingBox(PhysicalRect):
    """
    Синтаксический сахар
    Нужен, для удобного консертирования pymunk.BB в PhysicalRect
    """

    def __init__(self, bb: BB):
        super().__init__(x=bb.left,
                         y=bb.bottom,
                         width=bb.right - bb.left,
                         height=bb.top - bb.bottom)
