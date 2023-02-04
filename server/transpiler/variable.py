from server.transpiler.pyduino_utils import *

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

    def to_int(self):
        return False, f"Cannot convert {self.name} to int"

    def to_float(self):
        return False, f"Cannot convert {self.name} to float"

    def to_string(self):
        return False, f"Cannot convert {self.name} to string"

    def to_bool(self):
        return False, f"Cannot convert {self.name} to bool"

    def to_array(self):
        return False, f"Cannot convert {self.name} to array"

    def get_item(self, index: 'PyduinoType'):
        return False, f"Cannot get item {index} from {self.name}"

    def is_type(self, other: 'PyduinoType'):
        return str(self) == str(other)

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
        for type in [PyduinoBool, PyduinoInt, PyduinoFloat, PyduinoString, PyduinoArray, PyduinoVoid]:
            t = type.check_type(str)
            if t:
                return t
        return False

    @staticmethod
    def get_type_from_string(name: str) -> 'PyduinoType | bool':
        """
        Returns the type of the typename in the string (for example "int" or "float")
        :param self:
        :param str:
        :return:
        """
        for type in [PyduinoBool(), PyduinoInt(), PyduinoFloat(), PyduinoString(), PyduinoArray, PyduinoVoid()]:
            if type.is_typename(name):
                return type.is_typename(name)
        return False

    def is_typename(self, name: str) -> 'PyduinoType':
        if str(self) == name:
            return type(self)()
        return False

    def copy(self) -> 'PyduinoType':
        # TODO returns type without name
        return type(self)()


class PyduinoAny(PyduinoType):
    @staticmethod
    def check_type(str: str):
        return False


class PyduinoUndefined(PyduinoType):
    @staticmethod
    def check_type(str: str):
        return False

    def __str__(self):
        return "undefined"


class PyduinoVoid(PyduinoType):
    @staticmethod
    def check_type(str: str):
        if str == "void":
            return PyduinoVoid()
        return False

    def __str__(self):
        return "void"


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

    def to_string(self):
        return True, PyduinoString(f"String({self.name})")

    def to_int(self):
        return True, PyduinoInt(f"({self.name} ? 1 : 0)")

    def to_float(self):
        return True, PyduinoFloat(f"({self.name} ? 1.0 : 0.0)")

    def to_bool(self):
        return True, self

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

    def to_string(self):
        return True, PyduinoString(f"String({self.name})")

    def to_int(self):
        return True, self

    def to_float(self):
        return True, PyduinoFloat(f"(float){self.name}")

    def to_bool(self):
        return True, PyduinoBool(f"({self.name} != 0)")

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

    def to_string(self):
        return True, PyduinoString(f"String({self.name})")

    def to_int(self):
        return True, PyduinoInt(f"(int){self.name}")

    def to_float(self):
        return True, self

    def to_bool(self):
        return True, PyduinoBool(f"({self.name} != 0)")

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
            return True, PyduinoString(f"({self.name} + String({other.name}))")
        if str(other) == "float":
            return True, PyduinoString(f"({self.name} + String({other.name}))")
        if str(other) == "bool":
            return True, PyduinoString(f"({self.name} + String({other.name}))")
        if str(other) == "str":
            return True, PyduinoString(f"({self.name} + {other.name})")

        return False, f"Cannot add {other} to string"

    def to_string(self):
        return True, self.copy()

    def to_bool(self):
        return True, PyduinoBool(f"({self.name} != \"\")")

    def equal(self, other):
        if str(other) == "str":
            return True, PyduinoBool(f"({self.name} == {other.name})")
        return False, f"Cannot compare {other} to string"

    @staticmethod
    def check_type(str: str):
        if str[0] == '"' and str[-1] == '"':
            return PyduinoString(str)
        return False

    def __str__(self):
        return "str"


class PyduinoArray(PyduinoType):
    def __init__(self, item: PyduinoType, name: str = None, size: int = 0):
        super().__init__(name=name)
        self.item: PyduinoType = item
        self.size = size

    def len(self):
        return True, PyduinoInt(f"({self.name}.length())")

    def get_item(self, index: 'PyduinoType'):
        if str(index) != "int":
            return False, f"Cannot index array with {index}"
        item = self.item.copy()
        item.name = f"{self.name}[{index.name}]"
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

    def to_string(self):
        return True, PyduinoString(f"String({self.name})")

    def to_bool(self):
        return True, PyduinoBool(f"({self.name}.length() != 0)")

    def dimensions(self):
        dimensions = []
        dimensions.append(self.size)
        if self.item.is_iterable():
            dimensions += self.item.dimensions()
        return dimensions

    @staticmethod
    def is_typename(name: str) -> 'PyduinoType':
        if name.endswith("[]"):
            item = PyduinoType.get_type_from_string(name[:-2])
            if item:
                return PyduinoArray(item)
        return False

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

        # resolve brackets
        values = StringUtils.splitOutsideBrackets(value, transpiler.data.OPERATORS + ["not"], True)
        values = [v.strip() for v in values]

        for i, v in enumerate(values):
            if v.startswith("(") and v.endswith(")"):
                values[i] = Value.do_value(v[1:-1], transpiler)
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
            return Value.do_value_single(value, transpiler)

    @staticmethod
    def do_value_single(value: str, transpiler: 'Transpiler') -> 'Constant | Variable':
        """
        The value has to be a single value, no operators
        :param value:
        :param transpiler:
        :return:
        """

        t = PyduinoType.check_type(value)
        if t: return Constant(t.name, t)

        var = transpiler.scope.get_Variable(value, transpiler.location.position)
        if var: return var

        # check if it is a getitem
        for i in range(len(value) - 1):
            if value[i] in transpiler.data.VALID_NAME_END_CHARACTERS and value[i + 1] == "[":
                var = transpiler.scope.get_Variable(value[:i + 1], transpiler.location.position)
                if var:
                    indices = StringUtils.splitOutsideBrackets(value[i + 1:], ["[]"], True, split_after_brackets=True)
                    for id in indices:
                        if not (id[0] == "[" and id[-1] == "]"):
                            transpiler.data.newError(f"Invalid index {id}", transpiler.location.range)
                            transpiler.data.invalid_line_fallback.fallback(transpiler)

                    indices = [Value.do_value(id[1:-1], transpiler) for id in indices]
                    value = var
                    for ind in indices:
                        possible, value = value.type.get_item(ind.type)
                        if not possible:
                            transpiler.data.newError(value, transpiler.location.range)
                            transpiler.data.invalid_line_fallback.fallback(transpiler)
                        value = Constant(value.name, value)
                    return value
        # check if it is a function call

        transpiler.data.newError(f"Invalid value {value}", transpiler.location.range)
        transpiler.data.invalid_line_fallback.fallback(transpiler)


class Constant(Value):
    pass


class Variable(Value):
    @staticmethod
    def check_definition(instruction: str, transpiler: 'Transpiler') -> bool:
        line = transpiler.location.position.line
        instruction_range = Range(line, 0, complete_line=True, data=transpiler.data)
        operator_location = transpiler.utils.searchOutsideBrackets("=", range=instruction_range, fallback=StringNotFound_DoNothing)

        if not operator_location:
            return False

        equal = transpiler.data.getCode(Range(line, operator_location.col - 1, line, operator_location.col + 1))
        if equal[0] == "=" or equal[-1] == "=":
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

        value = Value.do_value(value, transpiler)
        variable = Variable(name, value.type)
        c_value = value.type.name
        value.type.name = name

        if str(value.type) != datatype:
            transpiler.data.newError(f"Variable '{name}' is of type '{value.type}' but should be of type '{datatype}'", name_range)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        if not StringUtils.is_identifier(name):
            transpiler.data.newError(f"'{name}' is not a valid variable name", name_range)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        if transpiler.scope.get_Variable(name, name_range.start):
            transpiler.data.newError(f"Variable '{name}' is already defined", name_range)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        if value.type.is_iterable():
            base_type = datatype.split("[")[0]
            c_code = f"{base_type} {name}{''.join(f'[{i}]' for i in value.type.dimensions())} = {c_value};"
        else:
            c_code = f"{datatype} {name} = {c_value};"

        transpiler.scope.add_Variable(variable, name_range.start)
        transpiler.data.code_done.append(c_code)

        return True


if __name__ == '__main__':
    print(PyduinoType.check_type("[[1,2,3                  ],[1,2,3],[1,2,3]]").name)
    print(PyduinoType.check_type("1").name)
