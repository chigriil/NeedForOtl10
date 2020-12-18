from os import PathLike
from typing import Union

import pygame

from Engine.Scene.animations import State
from Engine.utils.utils import load_yaml
from settings import default_sounds_path, persons_volume, global_volume, sounds_volume

default_config = load_yaml(default_sounds_path)


class EntitySounds:
    def __init__(self, entity):
        self.entity = entity
        self.__state = State.IDLE

        # self.idle = pygame.mixer.Sound(file=open(default_config['idle']['file']))
        #
        # self.walking = pygame.mixer.Sound(file=open(default_config['walking']['file']))
        #
        # self.running = pygame.mixer.Sound(file=open(default_config['running']['file']))
        #
        # self.sitting = pygame.mixer.Sound(file=open(default_config['sitting']['file']))
        #
        # self.squatting = pygame.mixer.Sound(file=open(default_config['squatting']['file']))
        #
        # self.lying = pygame.mixer.Sound(file=open(default_config['lying']['file']))
        #
        # self.crawling = pygame.mixer.Sound(file=open(default_config['crawling']['file']))
        #
        # self.soaring = pygame.mixer.Sound(file=open(default_config['soaring']['file']))
        #
        # self.jumping = pygame.mixer.Sound(file=open(default_config['jumping']['file']))
        #
        # self.flying = pygame.mixer.Sound(file=open(default_config['flying']['file']))
        #
        # self.landing = pygame.mixer.Sound(file=open(default_config['landing']['file']))
        #
        # self.throw = pygame.mixer.Sound(file=open(default_config['throw']['file']))
        #
        # self.hand_hit = pygame.mixer.Sound(file=open(default_config['hand_hit']['file']))

        self.load_sounds(default_sounds_path)

        self.last_playing = 'idle'

    def load_sounds(self, file_with_names: Union[str, bytes, PathLike[str], PathLike[bytes], int]):
        config = load_yaml(file_with_names)
        if not isinstance(config, dict):
            return
        for state, cfg in config.items():
            with open(cfg['file']) as sound_file:
                self.__dict__[state] = pygame.mixer.Sound(file=sound_file)
                self.__dict__[state].set_volume(cfg['volume'] * persons_volume * sounds_volume * global_volume)

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, new_state):
        if self.__state == new_state:
            return
        val = new_state.value

        if new_state == State.FLYING:
            val = 'flying'

        self.__dict__[self.last_playing].stop()
        self.__state = new_state
        self.last_playing = val
        self.__dict__[self.last_playing].play(-1)

    def play_single(self, name):
        self.__dict__[name].play()

    def step(self, dt):
        pass
