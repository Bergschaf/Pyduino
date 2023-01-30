from pyduino_types import *
from value import Value
if TYPE_CHECKING:
    from transpiler import Transpiler

class Variable:
    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def check_definition(transpiler: 'Transpiler',instruction: str, line: int) -> bool:
        instruction_range = Range(line, 0, complete_line=True, data=transpiler.data)
        operator_location = transpiler.utils.searchOutsideBrackets("=", range=instruction_range,fallback=StringNotFound_DoNothing)
        if not operator_location:
            return False

        split = instruction.split("=")
        left = split[0].strip().split(" ")
        if len(left) != 2:
            transpiler.data.newError(f"Invalid variable definition", instruction_range)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        datatype, name = left
        datatype, name = datatype.strip(), name.strip()

        value = "=".join(split[1:]).strip()

        name_range = transpiler.location.getRangeFromString(name)

        if not Value.is_identifier(name):
            transpiler.data.newError(f"'{name}' is not a valid variable name", name_range)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        if transpiler.scope.get_Variable(name, name_range.start, fallback=StringNotFound_DoNothing):
            transpiler.data.newError(f"Variable '{name}' is already defined", name_range)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        # validate datatype
        for key in Types.keys():
            if datatype.startswith(key):
                array_def = datatype[len(key):]
                if array_def:
                    if len(array_def) % 2 != 0:
                        transpiler.data.newError(f"Invalid array definition", transpiler.location.getRangeFromString(array_def))
                        transpiler.data.invalid_line_fallback.fallback(transpiler)
                        return True

                    for i in range(0,len(array_def),2):
                        if array_def[i] != "[" or array_def[i+1] != "]":
                            transpiler.data.newError(f"Invalid array definition", transpiler.location.getRangeFromString(array_def))
                            transpiler.data.invalid_line_fallback.fallback(transpiler)
                            return True

                    var = Types[key](name)
                    for _ in range(len(array_def)//2):
                        var = PyduinoArray(var, name)
                    break
                else:
                    var = Types[key](name)
                    break
        else:
            transpiler.data.newError(f"Invalid datatype '{datatype}'", transpiler.location.getRangeFromString(datatype))
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        transpiler.scope.add_Variable(var, name_range.start)
        return True


class PyduinoType(ABC,Variable):

    @abstractmethod
    def len(self):
        """(True if possible, False if not possible), (C Code for getting length of Datatype or the Error Message), return Type"""
        pass

    @abstractmethod
    def add(self,other):
        """(True if possible, False if not possible), C Code for adding the Datatypes, return Type"""
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
    def divmod(self,other):
        """
        the type is the left side of the divmod
        :return:
        """
        pass


class PyduinoInt(PyduinoType):
    def len(self):
        return False, "Cannot get length of int", None

    def add(self,other):
        if str(other) is self.__str__():
            return True, "({} + {})", PyduinoInt
        if other is PyduinoFloat:
            return True, "((float){} + {})", PyduinoFloat
        if other is PyduinoString:
            return True, "String({}) + {}", PyduinoString
        return False, f"Cannot add {other} to int", None

    def sub(self,other):
        if other is PyduinoInt:
            return True, "({} - {})", PyduinoInt
        if other is PyduinoFloat:
            return True, "((float){} - {})", PyduinoFloat
        return False, f"Cannot subtract {other} from int", None

    def mul(self,other):
        if other is PyduinoInt:
            return True, "({} * {})", PyduinoInt
        if other is PyduinoFloat:
            return True, "((float){} * {})", PyduinoFloat
        return False, f"Cannot multiply int with {other}", None

    def div(self,other):
        if other is PyduinoInt:
            return True, "((float){} / (float){})", PyduinoFloat
        if other is PyduinoFloat:
            return True, "((float){} / {})", PyduinoFloat
        return False, f"Cannot divide int by {other}", None

    def divmod(self,other):
        if other is PyduinoInt:
            return True, "({} % {})", PyduinoInt
        return False, f"Cannot get the remainder of int and {other}", None

    def __str__(self):
        return "int"

class PyduinoFloat(PyduinoType):
    def len(self):
        return False, "Cannot get length of float", None

    def add(self,other):
        if other is PyduinoInt:
            return True, "({} + (float){})", PyduinoFloat
        if other is PyduinoFloat:
            return True, "({} + {})", PyduinoFloat
        if other is PyduinoString:
            return True, "String({}) + {}", PyduinoString
        return False, f"Cannot add {other} to float", None

    def sub(self,other):
        if other is PyduinoInt:
            return True, "({} - (float){})", PyduinoFloat
        if other is PyduinoFloat:
            return True, "({} - {})", PyduinoFloat
        return False, f"Cannot subtract {other} from float", None

    def mul(self,other):
        if other is PyduinoInt:
            return True, "({} * (float){})", PyduinoFloat
        if other is PyduinoFloat:
            return True, "({} * {})", PyduinoFloat
        return False, f"Cannot multiply float with {other}", None

    def div(self,other):
        if other is PyduinoInt:
            return True, "({} / (float){})", PyduinoFloat
        if other is PyduinoFloat:
            return True, "({} / {})", PyduinoFloat
        return False, f"Cannot divide float by {other}", None

    def divmod(self,other):
        if other is PyduinoInt:
            return True, "((float){} % (float){})", PyduinoFloat
        return False, f"Cannot get the remainder of float and {other}", None

    def __str__(self):
        return "float"


class PyduinoString(PyduinoType):
    iterable = False
    def len(self):
        return True, "{}.length()", PyduinoInt

    def add(self,other):
        if other is PyduinoInt:
            return True, "String({}) + String({})", PyduinoString
        if other is PyduinoFloat:
            return True, "String({}) + String({})", PyduinoString
        if other is PyduinoString:
            return True, "String({}) + {}", PyduinoString
        return False, f"Cannot add {other} to string", None

    def sub(self,other):
        return False, f"Cannot subtract {other} from string", None

    def mul(self,other):
        return False, f"Cannot multiply string with {other}", None

    def div(self,other):
        return False, f"Cannot divide string by {other}", None

    def divmod(self,other):
        return False, f"Cannot get the remainder of string and {other}", None

    def __str__(self):
        return "string"


class PyduinoArray(PyduinoType):
    def __init__(self, item: PyduinoType, name: str):
        super().__init__(name)
        self.item:PyduinoType = item

    def add(self,other):
        return False, f"Cannot add {other} to array", None

    def len(self):
        return True, "{}.length()", PyduinoInt

    def sub(self,other):
        return False, f"Cannot subtract {other} from array", None

    def mul(self,other):
        return False, f"Cannot multiply array with {other}", None

    def div(self,other):
        return False, f"Cannot divide array by {other}", None

    def divmod(self,other):
        return False, f"Cannot get the remainder of array and {other}", None

    def __str__(self):
        return f"{self.item}[]"


Types = {"int": PyduinoInt, "float": PyduinoFloat, "str": PyduinoString}











