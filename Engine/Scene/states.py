from enum import Enum


class State(Enum):
    """
    Класс сотояний игрока, названия говорят сами за себя
    """
    IDLE = 'idle'  # ничего не делает

    WALKING = 'walking'  # идёт

    RUNNING = 'running'  # бежит

    SITTING = 'sitting'  # сидит на кортах

    SQUATTING = 'squatting'  # двигается на кортах

    LYING = 'lying'  # лежит

    CRAWLING = 'crawling'  # ползёт лёжа

    SOARING = 'soaring'  # парит в воздухе

    JUMPING = 'jumping'  # прыжок

    FLYING = 'flying'  # летит(в свободном падении)

    LANDING = 'landing'  # приземление

    DYING = 'dying'

    WIN = 'win'

