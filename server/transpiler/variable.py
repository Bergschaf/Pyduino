from server.transpiler.pyduino_utils import *
from server.transpiler.tokenizer import *

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

    def to_string(self) -> 'tuple[bool,PyduinoType]':
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

    def is_type(self, other: 'PyduinoType'):
        return True

    def __str__(self):
        return "any"


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
        return True, PyduinoInt(f"(sizeof({self.name}) / sizeof({self.name}[0]))")

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
        if type(items[0]) is PyduinoArray:
            if not all(items[0].size == item.size for item in items):
                return False
        while "  " in string:
            string = string.replace("  ", " ")

        return PyduinoArray(items[0], size=len(items), name=string.replace("[", "{").replace("]", "}"))

    def is_iterable(self):
        return True

    def to_string(self):
        if not self.item.is_iterable():
            return True, PyduinoString(f"arrayToString({self.name}, {self.len()[1].name})")
        else:
            # TODO return: "int[2][2]" (Datatype and Dimensions)
            depth = len(self.dimensions())
            quote = '"'
            first = "[0]"
            dimensions = f"{''.join([f' + {quote}[{quote} + String(sizeof({self.name}{first * i}) / sizeof({self.name}{first * (i + 1)})) + {quote}]{quote}' for i in range(depth)])}"
            return True, PyduinoString(f'"{self.name}"{dimensions}')

    def to_bool(self):
        return True, PyduinoBool(f"({self.len()[1].name} != 0)")

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

    def __init__(self, name: str, type: PyduinoType, location: 'Range'):
        self.name = name
        self.type = type
        self.type.name = name
        self.location = location

    @staticmethod
    def do_value(values: list['Token'], transpiler: 'Transpiler') -> 'Constant | Variable':
        # concentrate the values and algorithms
        last_operator = 0
        new_values = []
        for i in range(len(values)):
            if values[i].type in transpiler.data.OPERATORS:
                new_values.append(Value.do_value_single(values[last_operator:i], transpiler))
                new_values.append(values[i])
                last_operator = i + 1

        if last_operator == 0:
            return Value.do_value_single(values, transpiler)

        new_values.append(Value.do_value_single(values[last_operator:], transpiler))
        values = new_values

        for index, o in enumerate(transpiler.data.OPERATION_ORDER):
            shift_left = 0
            if index == 3:
                # check for not
                for i in range(1, len(values)):
                    if values[i - 1].type == Bool_Operator.NOT:
                        possible, t = values[i].type.not_()
                        if possible:
                            values[i] = Constant(t.name, t, Range.fromPositions(values[i - 1].location.start, values[i].location.end))
                            del values[i - 1]
                            shift_left += 2
                        else:
                            transpiler.data.newError(t, transpiler.location.range)
                            transpiler.data.invalid_line_fallback()
            shift_left = 0

            for i in range(1, len(values) - 1):
                i -= shift_left
                if values[i].type in o:
                    possible, t = values[i - 1].type.operator(values[i].type.name, values[i + 1].type)
                    if possible:
                        values[i - 1] = Constant(t.name, t, Range.fromPositions(values[i - 1].location.start, values[i + 1].location.end))
                        del values[i]
                        del values[i]
                        shift_left += 2
                    else:
                        transpiler.data.newError(t, values[i + 1].location)
                        transpiler.data.invalid_line_fallback()

        if len(values) > 1:
            raise Exception("Invalid value")
        return values[0]

    @staticmethod
    def do_value_single(value: list[Token], transpiler: 'Transpiler') -> 'Constant | Variable':
        """
        The value has to be a single value, no operators
        :param value:
        :param transpiler:
        :return:
        """
        if len(value) == 0:
            transpiler.data.newError(f"Invalid value None", transpiler.location.position)
            transpiler.data.invalid_line_fallback.fallback(transpiler)

        elif len(value) == 1:
            v = value[0]
            if v.type == Word.IDENTIFIER:
                # check if it is a variable
                var = transpiler.scope.get_Variable(v.value, v.location.start)
                if var:
                    return var

            if v.type == Word.VALUE or v.type == Word.IDENTIFIER:
                t = PyduinoType.check_type(v.value)
                if t:
                    return Constant(t.name, t, v.location)

            elif v.type == Brackets.ROUND:
                return Value.do_value(v.inside, transpiler)


        else:
            # check function call

            # check if it is a getitem
            if value[0].type == Word.IDENTIFIER:
                if all([v.type == Brackets.SQUARE for v in value[1:]]):
                    # it is a getitem
                    var = transpiler.scope.get_Variable(value[0].value, value[0].location.start)
                    indices = [Value.do_value(b.inside, transpiler) for b in value[1:]]
                    if var:
                        for i in range(len(value) - 1, 1, -1):
                            var = var.type.get_item(indices[i - 2].type)
                            if not var:
                                error = var
                                value[0].location = value[i].location
                                break
                        return Constant(var.name, var, Range.fromPositions(value[0].location.start, value[-1].location.end))

        transpiler.data.newError(f"Invalid value {value[0].value}", value[0].location)
        transpiler.data.invalid_line_fallback.fallback(transpiler)


class Constant(Value):
    pass


class Variable(Value):
    @staticmethod
    def check_definition(instruction: list[Token], transpiler: 'Transpiler') -> bool:
        line = transpiler.location.position.line
        instruction_range = Range(line, 0, complete_line=True, data=transpiler.data)
        operator_location = transpiler.utils.searchOutsideBrackets("=", range=instruction_range,
                                                                   fallback=StringNotFound_DoNothing)

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
            transpiler.data.newError(f"Variable '{name}' is of type '{value.type}' but should be of type '{datatype}'",
                                     name_range)
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
