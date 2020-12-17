# Разрешение экрана
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

# скорость, ниже которой модули всех скоростей считются нулём
critical_speed = 1e-2

# косинус угола между реакцией опоры(которая не равна 0) и нормалью, при которой считается устройчивая опора для ног
# Коэффициент трения = sqrt(1/critical_ground_collision**2 - 1)
critical_ground_collision = 0.35

# Максимальная скорость отскока от земли, при которой не засчитывается полёт
# Не должна быть слишком большой, иначе не будет ощущения, что игрок сразу начинает падать, при отсутствии опоры для ног
# Не должна быть маленькой, иначе будуь засчитываться ложные смены статуса на полёт
bounce_correction_speed = 1

# Критический уровень перезарядки, при котором уже можно снова ипользовать способность
critical_reloading = 0.01

# отклонение от угла, при котором не происоходит перерисовывание
no_rotate_delta = 0.1

# Ускорение свободного падения
g = 9.81

# Режим разработчика по умолчанию
DEVMODE = True

# Путь до папки с конфигарациями персонажей
person_configs_path = 'src/configs/persons'

# Путь до папки с конфигарациями статичных объектов
game_objects_configs_path = 'src/configs/game_objects'
