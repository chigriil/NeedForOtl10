"""
Класс содержащий геометрическое примитивы из физической реализации сцены
"""


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
    def bottomleft(self):
        """
        Возвращает координаты левого нижнего угла прямоугольника
        TODO: допилить такие же свойства для других углов, середин сторон и центра. Делать по ходу необходимости
        :return: координаты левого нижнего угла прямоугольника
        """
        return [self.x, self.y]

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
        :return: картеж (ширина, высота)
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
