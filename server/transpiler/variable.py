from pyduino_types import *


class Variable:

    def __init__(self, name: str, type: type[PyduinoType]):
        self.name = name
        self.type = type
