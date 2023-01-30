from pyduino_utils import *

if TYPE_CHECKING:
    from transpiler import Transpiler


class PyduinoType():
    def __init__(self, name: str = None):
        self.name = name

    def operator(self, operator: str, other: 'PyduinoType'):
        MAP = {
            "+": self.add,
            "-": self.sub,
            "*": self.mul,
            "/": self.div,
            "%": self.divmod,
            "and": self.and_,
            "or": self.or_,
            ">": self.greater,
            "<": self.less,
            ">=": self.greater_equal,
            "<=": self.less_equal,
            "==": self.equal,
            "!=": self.not_equal}

        return MAP[operator](other)

    def len(self):
        """(True if possible, False if not possible), return Value with C code"""
        return False, f"Cannot get the length of {self.name}"

    def add(self, other: 'PyduinoType'):
        return False, f"Cannot add {self.name} and {other.name}"

    def sub(self, other: 'PyduinoType'):
        return False, f"Cannot subtract {self.name} and {other.name}"

    def mul(self, other: 'PyduinoType'):
        return False, f"Cannot multiply {self.name} and {other.name}"

    def div(self, other: 'PyduinoType'):
        return False, f"Cannot divide {self.name} and {other.name}"

    def divmod(self, other: 'PyduinoType'):
        """
        the type is the left side of the divmod
        :return:
        """
        return False, f"Cannot get the remainder {self.name} and {other.name}"

    def and_(self, other: 'PyduinoType'):
        return False, f"Cannot use the 'and' operator on {self.name} and {other.name}"

    def or_(self, other: 'PyduinoType'):
        return False, f"Cannot use the 'or' operator on {self.name} and {other.name}"

    def greater(self, other: 'PyduinoType'):
        return False, f"Cannot compare {self.name} and {other.name}"

    def less(self, other: 'PyduinoType'):
        return False, f"Cannot compare {self.name} and {other.name}"

    def greater_equal(self, other: 'PyduinoType'):
        return False, f"Cannot compare {self.name} and {other.name}"

    def less_equal(self, other: 'PyduinoType'):
        return False, f"Cannot compare {self.name} and {other.name}"

    def equal(self, other: 'PyduinoType'):
        return False, f"Cannot compare {self.name} and {other.name}"

    def not_equal(self, other: 'PyduinoType'):
        return False, f"Cannot compare {self.name} and {other.name}"

    def not_(self):
        return False, f"Cannot negate {self.name}"

    def is_iterable(self):
        return False

    def dimensions(self):
        return []

    @staticmethod
    def check_type(str: str) -> 'PyduinoType':
        """
        Checks if the value in the string belongs to the type, returns an object if it does
        :param str:
        :return:
        """
        for type in [PyduinoBool, PyduinoInt, PyduinoFloat, PyduinoString, PyduinoArray]:
            t = type.check_type(str)
            if t:
                return t
        return False

    def copy(self) -> 'PyduinoType':
        # TODO returns type without name
        return type(self)()


class PyduinoAny(PyduinoType):
    @staticmethod
    def check_type(str: str):
        return False


class PyduinoBool(PyduinoType):
    def and_(self, other):
        if str(other) == "bool":
            return True, PyduinoBool(f"({self.name} && {other.name})")
        return False, f"Cannot and {other} with bool"

    def or_(self, other):
        if str(other) == "bool":
            return True, PyduinoBool(f"({self.name} || {other.name})")
        return False, f"Cannot or {other} with bool"

    def equal(self, other):
        if str(other) == "bool":
            return True, PyduinoBool(f"({self.name} == {other.name})")
        return False, f"Cannot compare {other} to bool"

    def not_equal(self, other):
        if str(other) == "bool":
            return True, PyduinoBool(f"({self.name} != {other.name})")
        return False, f"Cannot compare {other} to bool"

    def not_(self):
        return True, PyduinoBool(f"!{self.name}")

    @staticmethod
    def check_type(string: str) -> 'PyduinoType':
        if string == "True" or string == "False":
            return PyduinoBool(string.lower())
        return False

    def __str__(self):
        return "bool"


class PyduinoInt(PyduinoType):
    def add(self, other):
        if str(other) == "int":
            return True, PyduinoInt(f"({self.name} + {other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"((float){self.name} + {other.name})")
        if str(other) == "str":
            return True, PyduinoString(f"(String({self.name}) + {other.name})")
        return False, f"Cannot add {other} to int"

    def sub(self, other):
        if str(other) == "int":
            return True, PyduinoInt(f"({self.name} - {other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"((float){self.name} - {other.name})")
        return False, f"Cannot subtract {other} from int"

    def mul(self, other):
        if str(other) == "int":
            return True, PyduinoInt(f"({self.name} * {other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"((float){self.name} * {other.name})")
        return False, f"Cannot multiply int with {other}"

    def div(self, other):
        if str(other) == "int":
            return True, PyduinoFloat(f"((float){self.name} / (float){other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"((float){self.name} / {other.name})")
        return False, f"Cannot divide int by {other}"

    def divmod(self, other):
        if str(other) == "int":
            return True, PyduinoInt(f"({self.name} % {other.name})")
        return False, f"Cannot get the remainder of int and {other}"

    def greater(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} > {other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"((float){self.name} > {other.name})")
        return False, f"Cannot compare {other} to int"

    def less(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} < {other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"((float){self.name} < {other.name})")
        return False, f"Cannot compare {other} to int"

    def greater_equal(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} >= {other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"((float){self.name} >= {other.name})")
        return False, f"Cannot compare {other} to int"

    def less_equal(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} <= {other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"((float){self.name} <= {other.name})")
        return False, f"Cannot compare {other} to int"

    def equal(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} == {other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"((float){self.name} == {other.name})")
        return False, f"Cannot compare {other} to int"

    def not_equal(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} != {other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"((float){self.name} != {other.name})")
        return False, f"Cannot compare {other} to int"

    @staticmethod
    def check_type(str: str):
        if str.isdigit():
            return PyduinoInt(str)
        return False

    def __str__(self):
        return "int"


class PyduinoFloat(PyduinoType):
    def add(self, other):
        if str(other) == "int":
            return True, PyduinoFloat(f"({self.name} + (float){other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"({self.name} + {other.name})")
        if str(other) == "str":
            return True, PyduinoString(f"(String({self.name}) + {other.name})")
        return False, f"Cannot add {other} to float"

    def sub(self, other):
        if str(other) == "int":
            return True, PyduinoFloat(f"({self.name} - (float){other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"({self.name} - {other.name})")
        return False, f"Cannot subtract {other} from float"

    def mul(self, other):
        if str(other) == "int":
            return True, PyduinoFloat(f"({self.name} * (float){other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"({self.name} * {other.name})")
        return False, f"Cannot multiply float with {other}"

    def div(self, other):
        if str(other) == "int":
            return True, PyduinoFloat(f"({self.name} / (float){other.name})")
        if str(other) == "float":
            return True, PyduinoFloat(f"({self.name} / {other.name})")
        return False, f"Cannot divide float by {other}",

    def greater(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} > (float){other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"({self.name} > {other.name})")
        return False, f"Cannot compare {other} to float"

    def less(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} < (float){other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"({self.name} < {other.name})")
        return False, f"Cannot compare {other} to float"

    def greater_equal(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} >= (float){other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"({self.name} >= {other.name})")
        return False, f"Cannot compare {other} to float"

    def less_equal(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} <= (float){other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"({self.name} <= {other.name})")
        return False, f"Cannot compare {other} to float"

    def equal(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} == (float){other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"({self.name} == {other.name})")
        return False, f"Cannot compare {other} to float"

    def not_equal(self, other):
        if str(other) == "int":
            return True, PyduinoBool(f"({self.name} != (float){other.name})")
        if str(other) == "float":
            return True, PyduinoBool(f"({self.name} != {other.name})")
        return False, f"Cannot compare {other} to float"

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

    def len(self):
        return True, PyduinoInt(f"({self.name}.length())")

    def getitem(self, id: PyduinoType):
        item = self.item.copy()
        item.name = f"{self.name}[{id.name}]"
        return True, item

    @staticmethod
    def check_type(string: str):
        # TODO add error messages
        if not string.startswith("[") or not string.endswith("]"):
            return False
        items = StringUtils.splitOutsideBrackets(string[1:-1], [","])
        if len(items) == 0:
            return PyduinoArray(PyduinoAny())
        items = [PyduinoType.check_type(item.strip()) for item in items]
        if False in items:
            return False
        if not all(str(items[0]) == str(item) for item in items):
            return False
        if type(items[0]) == PyduinoArray:
            if not all(items[0].size == item.size for item in items):
                return False
        while "  " in string:
            string = string.replace("  ", " ")

        return PyduinoArray(items[0], size=len(items), name=string.replace("[", "{").replace("]", "}"))

    def is_iterable(self):
        return True

    def dimensions(self):
        dimensions = []
        dimensions.append(self.size)
        if self.item.is_iterable():
            dimensions += self.item.dimensions()
        return dimensions

    def __str__(self):
        return f"{self.item}[]"

    def copy(self) -> 'PyduinoArray':
        return PyduinoArray(self.item.copy())


Types = {"int": PyduinoInt, "float": PyduinoFloat, "str": PyduinoString}


class Value:

    def __init__(self, name: str, type: PyduinoType):
        self.name = name
        self.type = type

    @staticmethod
    def do_value(value: str, transpiler: 'Transpiler') -> 'Constant | Variable':
        # has to set location.position and location.range before calling
        # TODO add detailed errors, errors will always cover the complete value

        t = PyduinoType.check_type(value)
        if t: return Constant(t.name, t)

        var = transpiler.scope.get_Variable(value, transpiler.location.position)
        if var: return var

        # resolve brackets
        values = StringUtils.splitOutsideBrackets(value, transpiler.data.OPERATORS + ["not"], True)
        values = [v.strip() for v in values]

        for i,v in enumerate(values):
            if v.startswith("(") and v.endswith(")"):
                values[i] = Value.do_value(v[1:-1],transpiler)
                # check all the operators

        for o in transpiler.data.OPERATION_ORDER:
            shift_left = 0
            for i in range(1, len(values) - 1):
                i -= shift_left
                if values[i] in o:
                    if type(values[i - 1]) is str:
                        v1 = Value.do_value(values[i - 1], transpiler)
                    else:
                        v1 = values[i - 1]

                    if type(values[i + 1]) is str:
                        v2 = Value.do_value(values[i + 1], transpiler)
                    else:
                        v2 = values[i + 1]

                    if v1 and v2:
                        possible, t = v1.type.operator(values[i], v2.type)
                        if possible:
                            values[i - 1] = Constant(t.name, t)
                            del values[i]
                            del values[i]
                            shift_left += 2
                        else:
                            transpiler.data.newError(t, transpiler.location.range)
                            transpiler.data.invalid_line_fallback.fallback(transpiler)

        # check for not

        shift_left = 0
        for i in range(1, len(values)):
            i -= shift_left
            if values[i - 1] == "not":
                possible, t = values[i].type.not_()
                if possible:
                    values[i] = Constant(t.name, t)
                    del values[i - 1]
                    shift_left += 1
                else:
                    transpiler.data.newError(t, transpiler.location.range)
                    transpiler.data.invalid_line_fallback()

        if len(values) == 1 and type(values[0]) is not str:
            return values[0]
        else:
            transpiler.data.newError(f"Invalid value {values}", transpiler.location.range)
            transpiler.data.invalid_line_fallback.fallback(transpiler)


class Constant(Value):
    pass


class Variable(Value):
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

        if transpiler.scope.get_Variable(name, name_range.start):
            transpiler.data.newError(f"Variable '{name}' is already defined", name_range)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        value = Value.do_value(value, transpiler)
        variable = Variable(name, value.type)
        c_value = value.type.name
        value.type.name = name
        if str(value.type) != datatype:
            transpiler.data.newError(f"Variable '{name}' is of type '{value.type}' but should be of type '{datatype}'", name_range)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        if value.type.is_iterable():
            base_type = datatype.split("[")[0]
            c_code = f"{base_type} {name}{''.join(f'[{i}]' for i in value.type.dimensions())} = {c_value};"
        else:
            c_code = f"{datatype} {name} = {c_value};"

        transpiler.data.code_done.append(c_code)

        return True


if __name__ == '__main__':
    print(PyduinoType.check_type("[[1,2,3                  ],[1,2,3],[1,2,3]]").name)
    print(PyduinoType.check_type("1").name)
