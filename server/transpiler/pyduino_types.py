import typing

from pyduino_utils import *


class PyduinoType(ABC):

    @staticmethod
    @abstractmethod
    def len():
        """(True if possible, False if not possible), (C Code for getting length of Datatype or the Error Message), return Type"""
        pass

    @staticmethod
    @abstractmethod
    def add(other):
        """(True if possible, False if not possible), C Code for adding the Datatypes, return Type"""
        pass

    @staticmethod
    @abstractmethod
    def sub(other):
        pass

    @staticmethod
    @abstractmethod
    def mul(other):
        pass

    @staticmethod
    @abstractmethod
    def div(other):
        pass

    @staticmethod
    @abstractmethod
    def divmod(other):
        """
        the type is the left side of the divmod
        :return:
        """
        pass


class PyduinoInt(PyduinoType):
    @staticmethod
    def len():
        return False, "Cannot get length of int", None

    @staticmethod
    def add(other):
        if other is PyduinoInt:
            return True, "({} + {})", PyduinoInt
        if other is PyduinoFloat:
            return True, "((float){} + {})", PyduinoFloat
        if other is PyduinoString:
            return True, "String({}) + {}", PyduinoString
        return False, f"Cannot add {other} to int", None

    @staticmethod
    def sub(other):
        if other is PyduinoInt:
            return True, "({} - {})", PyduinoInt
        if other is PyduinoFloat:
            return True, "((float){} - {})", PyduinoFloat
        return False, f"Cannot subtract {other} from int", None

    @staticmethod
    def mul(other):
        if other is PyduinoInt:
            return True, "({} * {})", PyduinoInt
        if other is PyduinoFloat:
            return True, "((float){} * {})", PyduinoFloat
        return False, f"Cannot multiply int with {other}", None

    @staticmethod
    def div(other):
        if other is PyduinoInt:
            return True, "((float){} / (float){})", PyduinoFloat
        if other is PyduinoFloat:
            return True, "((float){} / {})", PyduinoFloat
        return False, f"Cannot divide int by {other}", None

    @staticmethod
    def divmod(other):
        if other is PyduinoInt:
            return True, "({} % {})", PyduinoInt
        return False, f"Cannot get the remainder of int and {other}", None

    def __str__(self):
        return "int"

class PyduinoFloat():
    @staticmethod
    def len():
        return False, "Cannot get length of float", None

    @staticmethod
    def add(other):
        if other is PyduinoInt:
            return True, "({} + (float){})", PyduinoFloat
        if other is PyduinoFloat:
            return True, "({} + {})", PyduinoFloat
        if other is PyduinoString:
            return True, "String({}) + {}", PyduinoString
        return False, f"Cannot add {other} to float", None

    @staticmethod
    def sub(other):
        if other is PyduinoInt:
            return True, "({} - (float){})", PyduinoFloat
        if other is PyduinoFloat:
            return True, "({} - {})", PyduinoFloat
        return False, f"Cannot subtract {other} from float", None

    @staticmethod
    def mul(other):
        if other is PyduinoInt:
            return True, "({} * (float){})", PyduinoFloat
        if other is PyduinoFloat:
            return True, "({} * {})", PyduinoFloat
        return False, f"Cannot multiply float with {other}", None

    @staticmethod
    def div(other):
        if other is PyduinoInt:
            return True, "({} / (float){})", PyduinoFloat
        if other is PyduinoFloat:
            return True, "({} / {})", PyduinoFloat
        return False, f"Cannot divide float by {other}", None

    @staticmethod
    def divmod(other):
        if other is PyduinoInt:
            return True, "((float){} % (float){})", PyduinoFloat
        return False, f"Cannot get the remainder of float and {other}", None

    def __str__(self):
        return "float"


class PyduinoString(PyduinoType):
    @staticmethod
    def len():
        return True, "{}.length()", PyduinoInt

    @staticmethod
    def add(other):
        if other is PyduinoInt:
            return True, "String({}) + String({})", PyduinoString
        if other is PyduinoFloat:
            return True, "String({}) + String({})", PyduinoString
        if other is PyduinoString:
            return True, "String({}) + {}", PyduinoString
        return False, f"Cannot add {other} to string", None

    @staticmethod
    def sub(other):
        return False, f"Cannot subtract {other} from string", None

    @staticmethod
    def mul(other):
        return False, f"Cannot multiply string with {other}", None

    @staticmethod
    def div(other):
        return False, f"Cannot divide string by {other}", None

    @staticmethod
    def divmod(other):
        return False, f"Cannot get the remainder of string and {other}", None

    def __str__(self):
        return "string"


class PyduinoArray(PyduinoType):
    def __init__(self,dtype:PyduinoType):
        self.dtype = dtype

    @staticmethod
    def add(other):
        return False, f"Cannot add {other} to array", None

    @staticmethod
    def len():
        return True, "{}.length()", PyduinoInt

    @staticmethod
    def sub(other):
        return False, f"Cannot subtract {other} from array", None

    @staticmethod
    def mul(other):
        return False, f"Cannot multiply array with {other}", None

    @staticmethod
    def div(other):
        return False, f"Cannot divide array by {other}", None

    @staticmethod
    def divmod(other):
        return False, f"Cannot get the remainder of array and {other}", None

    def __str__(self):
        return f"{self.dtype}[]"



Types = {"int": PyduinoInt(), "float": PyduinoFloat(), "string": PyduinoString(), "int[]": PyduinoArray(PyduinoInt()), "float[]": PyduinoArray(PyduinoFloat()),
         "string[]": PyduinoArray(PyduinoString())}

if __name__ == '__main__':
    print(str(Types["int"]))
    print(str(Types["float[]"]))
