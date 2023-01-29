from pyduino_utils import *

class Value:
    @staticmethod
    def do_value() -> str:
        pass

    @staticmethod
    def resolveBrackets(range:Range,location:CurrentLocation, data:Data) -> str:
        location.range = range
        location.position = range.start

        valueList = [] # List of values

    @staticmethod
    def is_identifier(value:str) -> bool:
        """
        :param value: The value to check
        :return: True if the value is an identifier, False if not
        """
        if value.isnumeric():
            return False
        for i in value:
            if not i.isalnum() and i != "_":
                return False
        return True




