from abc import ABC, abstractmethod
from pyduino_utils import *


class PyduinoType(ABC):
    @abstractmethod
    def len(self):
        """(True if possible, False if not possible), (C Code for getting length of Datatype or the Error Object)"""
        pass

    @abstractmethod
    def add(self, other):
        """(True if possible, False if not possible), C Code for adding the Datatypes"""
        pass

    @abstractmethod
    def sub(self,other):
        pass

    @abstractmethod
    def mul(self,other):
        pass

    @abstractmethod
    def div(self,other):
        pass

    @abstractmethod
    def divmod(self):
        pass

class PyduinoInt(PyduinoType):
    @staticmethod
    def len():
        return False, Error("Cannot get length of int", 0, 0)


