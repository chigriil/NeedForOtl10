from os import PathLike
from typing import Union, Any, Hashable

import PIL
import pygame


def get_time_for_save() -> str:


def load_yaml(path: Union[str, bytes, PathLike[str], PathLike[bytes], int]) -> \
        Union[dict[Hashable, Any], list, None]: ...


def save_yaml(obj: Union[dict[Hashable, Any], list, None],
              path: Union[str, bytes, PathLike[str], PathLike[bytes], int]) -> None: ...


def load_json(path: Union[str, bytes, PathLike[str], PathLike[bytes], int]) -> \
        Union[dict[Hashable, Any], list, None]: ...


def save_json(obj: Union[dict[Hashable, Any], list, None],
              path: Union[str, bytes, PathLike[str], PathLike[bytes], int]) -> None: ...


def load_image(path: Union[str, bytes, PathLike[str], PathLike[bytes], int]) -> PIL.PngImagePlugin.PngImageFile: ...


def pil_to_pygame(pil_image: PIL.PngImagePlugin.PngImageFile) -> pygame.Surface: ...
