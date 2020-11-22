"""
Класс содержащий геометрическое примитивы из физической реализации сцены
"""
from pymunk import Vec2d


class PhysicalRect:
    """
    Прямоугольник
    """

    def __init__(self, x, y, width, height):
        """
        :param x: координата x левого нижнего края прямоугольника
        :param y: координата н левого нижнего края прямоугольника
        :param width: ширина прямоугольника
        :param height: высота прямоугольника
        """
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height

    @property
    def centre(self):
        return Vec2d(self.__x + self.__width / 2,
                     self.__y + self.__height / 2)

    @property
    def bottomleft(self):
        """
        Возвращает координаты левого нижнего угла прямоугольника
        :return: координаты левого нижнего угла прямоугольника
        """
        return Vec2d(self.x,
                self.y)

    @property
    def topleft(self):
        """
        Возвращает координаты левого верхнего угла прямоугольника
        :return: координаты левого верхнего угла прямоугольника
        """
        return Vec2d(self.x,
                self.y + self.__height)

    @property
    def bottomright(self):
        """
        Возвращает координаты правого нижнего нижнего угла прямоугольника
        :return: координаты правого нижнего угла прямоугольника
        """
        return Vec2d(self.x + self.__width,
                self.y)

    @property
    def topright(self):
        """
        Возвращает координаты правого нижнего верхнего угла прямоугольника
        :return: координаты правого верхнего угла прямоугольника
        """
        return Vec2d(self.x + self.__width,
                self.y + self.__height)

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

    @property
    def topborder(self):
        return self.__y + self.__height

    @property
    def rightborder(self):
        return self.__x + self.__width

    @property
    def bottomborder(self):
        return self.__y

    @property
    def leftborder(self):
        return self.__x

    def vertices(self):
        return [
            self.topleft,
            self.topright,
            self.bottomright,
            self.bottomleft
        ]
