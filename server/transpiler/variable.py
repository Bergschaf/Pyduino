from pyduino_utils import *

if TYPE_CHECKING:
    from transpiler import Transpiler


class PyduinoType(ABC):
    def __init__(self, name: str = None):
        self.name = name

    @abstractmethod
    def len(self):
        """(True if possible, False if not possible), return Value with C code"""
        pass

    @abstractmethod
    def add(self, other: 'PyduinoType'):
        pass

    @abstractmethod
    def sub(self, other: 'PyduinoType'):
        pass

    @abstractmethod
    def mul(self, other: 'PyduinoType'):
        pass

    @abstractmethod
    def div(self, other: 'PyduinoType'):
        pass

    @abstractmethod
    def divmod(self, other: 'PyduinoType'):
        """
        the type is the left side of the divmod
        :return:
        """
        pass

    @staticmethod
    @abstractmethod
    def check_type(str: str):
        """
        Checks if the value in the string belongs to the type, returns an object if it does
        :param str:
        :return:
        """
        for type in PyduinoType.__subclasses__():
            t = type.check_type(str)
            if t:
                return t
        return False

    def copy(self) -> 'PyduinoType':
        # TODO returns type without name
        return type(self)()


class PyduinoAny(PyduinoType):
    def len(self):
        return False, "Cannot get length of any", None

    def add(self, other):
        return False, f"Cannot add {other} to any", None

    def sub(self, other):
        return False, f"Cannot subtract {other} from any", None

    def mul(self, other):
        return False, f"Cannot multiply {other} with any", None

    def div(self, other):
        return False, f"Cannot divide {other} by any", None

    def divmod(self, other):
        return False, f"Cannot divide {other} by any", None

    @staticmethod
    def check_type(str: str):
        return False


class PyduinoInt(PyduinoType):
    def len(self):
        return False, "Cannot get length of int", None

    def add(self, other):
        if str(other) == "int":
            return True, PyduinoInt(f"({self.name} + {other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"((float){self.name} + {other.name})")
        if str(other) == "str":
            return True, PyduinoString(f"(String({self.name}) + {other.name})")
        return False, f"Cannot add {other} to int", None

    def sub(self, other):
        if str(other) == "int":
            return True, PyduinoInt(f"({self.name} - {other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"((float){self.name} - {other.name})")
        return False, f"Cannot subtract {other} from int", None

    def mul(self, other):
        if str(other) == "int":
            return True, PyduinoInt(f"({self.name} * {other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"((float){self.name} * {other.name})")
        return False, f"Cannot multiply int with {other}", None

    def div(self, other):
        if str(other) == "int":
            return True, PyduinoFloat(f"((float){self.name} / (float){other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"((float){self.name} / {other.name})")
        return False, f"Cannot divide int by {other}", None

    def divmod(self, other):
        if str(other) == "int":
            return True, PyduinoInt(f"({self.name} % {other.name})")
        return False, f"Cannot get the remainder of int and {other}", None

    @staticmethod
    def check_type(str: str):
        if str.isdigit():
            return PyduinoInt(str)
        return False

    def __str__(self):
        return "int"


class PyduinoFloat(PyduinoType):
    def len(self):
        return False, "Cannot get length of float", None

    def add(self, other):
        if str(other) == "int":
            return True, PyduinoFloat(f"({self.name} + (float){other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"({self.name} + {other.name})")
        if str(other) == "str":
            return True, PyduinoString(f"(String({self.name}) + {other.name})")
        return False, f"Cannot add {other} to float", None

    def sub(self, other):
        if str(other) == "int":
            return True, PyduinoFloat(f"({self.name} - (float){other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"({self.name} - {other.name})")
        return False, f"Cannot subtract {other} from float", None

    def mul(self, other):
        if str(other) == "int":
            return True, PyduinoFloat(f"({self.name} * (float){other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"({self.name} * {other.name})")
        return False, f"Cannot multiply float with {other}", None

    def div(self, other):
        if str(other) == "int":
            return True, PyduinoFloat(f"({self.name} / (float){other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"({self.name} / {other.name})")
        return False, f"Cannot divide float by {other}", None

    def divmod(self, other):
        return False, f"Cannot get the remainder of float and {other}", None

    @staticmethod
    def check_type(str: str):
        if str.replace(".", "", 1).isdigit() and "." in str:
            return PyduinoFloat(str)
        return False

    def __str__(self):
        return "float"


class PyduinoString(PyduinoType):
    def len(self):
        return True, PyduinoInt(f"({self.name}.length())")

    def add(self, other):
        if str(other) == "int":
            return True, PyduinoString(f"(String({self.name}) + String({other.name}))")
        if str(other) == "float":
            return True, PyduinoString(f"(String({self.name}) + String({other.name}))")
        if str(other) == "str":
            return True, PyduinoString(f"(String({self.name}) + {other.name})")
        return False, f"Cannot add {other} to string", None

    def sub(self, other):
        return False, f"Cannot subtract {other} from string", None

    def mul(self, other):
        return False, f"Cannot multiply string with {other}", None

    def div(self, other):
        return False, f"Cannot divide string by {other}", None

    def divmod(self, other):
        return False, f"Cannot get the remainder of string and {other}", None

    @staticmethod
    def check_type(str: str):
        if str[0] == '"' and str[-1] == '"':
            return PyduinoString(str)
        return False

    def __str__(self):
        return "string"


class PyduinoArray(PyduinoType):
    def __init__(self, item: PyduinoType, name: str = None, size: int = 0):
        super().__init__(name=name)
        self.item: PyduinoType = item
        self.size = size

    def add(self, other):
        return False, f"Cannot add {other} to array", None

    def len(self):
        return True, PyduinoInt(f"{self.name}.length()")

    def sub(self, other):
        return False, f"Cannot subtract {other} from array", None

    def mul(self, other):
        return False, f"Cannot multiply array with {other}", None

    def div(self, other):
        return False, f"Cannot divide array by {other}", None

    def divmod(self, other):
        return False, f"Cannot get the remainder of array and {other}", None

    def getitem(self, id: PyduinoType):
        item = self.item.copy()
        item.name = f"{self.name}[{id.name}]"
        return True, item

    @staticmethod
    def check_type(string: str):
        if not string.startswith("[") or not string.endswith("]"):
            return False
        string = StringUtils.splitCommaOutsideBrackets(string[1:-1])
        if len(string) == 0:
            return PyduinoArray(PyduinoAny())
        items = [PyduinoType.check_type(item.strip()) for item in string]
        if False in items:
            return False
        if not all(str(items[0]) == str(item) for item in items):
            return False
        if type(items[0]) == PyduinoArray:
            if not all(items[0].size == item.size for item in items):
                return False
        return PyduinoArray(items[0], size=len(items))

    def __str__(self):
        return f"{self.item}[]"

    def copy(self) -> 'PyduinoArray':
        return PyduinoArray(self.item.copy())


Types = {"int": PyduinoInt, "float": PyduinoFloat, "str": PyduinoString}


class Value:

    def __init__(self, name: str, type: PyduinoType):
        self.name = name  # the C++ representation of the value (for example '1' or 'test[x]'
        self.type = type

    @staticmethod
    def do_value(value: str, transpiler: 'Transpiler') -> 'Value':
        # has to set location.position and location.range before calling
        # TODO add detailed errors, errors will always cover the complete value
        # TODO remove all unnecessary spaces
        # TODO IMPORTANT ^ for the check_type function, especially for ARRAYS
        PyduinoType.check_type(value)


class Variable:

    def __init__(self, name: str, type: 'PyduinoType'):
        self.name = name
        self.type = PyduinoType

    @staticmethod
    def check_definition(transpiler: 'Transpiler', instruction: str, line: int) -> bool:
        instruction_range = Range(line, 0, complete_line=True, data=transpiler.data)
        operator_location = transpiler.utils.searchOutsideBrackets("=", range=instruction_range, fallback=StringNotFound_DoNothing)
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

        if not StringUtils.is_identifier(name):
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

                    for i in range(0, len(array_def), 2):
                        if array_def[i] != "[" or array_def[i + 1] != "]":
                            transpiler.data.newError(f"Invalid array definition", transpiler.location.getRangeFromString(array_def))
                            transpiler.data.invalid_line_fallback.fallback(transpiler)
                            return True

                    var = Types[key]()
                    for _ in range(len(array_def) // 2):
                        var = PyduinoArray(var)
                    var.name = name
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


if __name__ == '__main__':
    print(PyduinoArray.check_type("[[1,2,3                  ],[1,2,3],[1,2.2,3]]"))
