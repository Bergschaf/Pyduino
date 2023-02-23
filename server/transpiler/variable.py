from server.transpiler.pyduino_utils import *
from server.transpiler.tokenizer import *

if TYPE_CHECKING:
    from transpiler import Transpiler


class PyduinoType():
    SIZE_BYTES = 0
    ARDUINO_BYTE_CONVERSION = ""
    C_TYPENAME = "Undefined"
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

    def plus_plus(self):
        return False, f"Cannot increment {self.name}"

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

    @staticmethod
    def bytes_to_type(buffer: str) -> 'tuple[bool, str | PyduinoType]':
        return False, f"Cannot convert bytes to this Type"

    def type_to_bytes(self) -> 'tuple[bool, str]':
        return False, f"Cannot convert {self.name} to bytes"

    def is_iterable(self):
        return False

    def dimensions(self):
        return []

    @staticmethod
    def check_type(value: Token, transpiler: 'Transpiler') -> 'PyduinoType':
        """
        Checks if the value in the string belongs to the type, returns an object if it does
        :param str:
        :return:
        """
        if value.type == Word.IDENTIFIER or value.type == Word.VALUE:
            for type in [PyduinoBool, PyduinoInt, PyduinoFloat, PyduinoString, PyduinoVoid]:
                t = type.check_type(value.value)
                if t:
                    return t
        elif value.type == Brackets.SQUARE:
            return PyduinoArray.check_type(value, transpiler)
        return False

    @staticmethod
    def get_type_from_token(tokens: list[Token]):
        if len(tokens) == 1:
            token = tokens[0]
            if token.type == Datatype.INT:
                return PyduinoInt()
            elif token.type == Datatype.FLOAT:
                return PyduinoFloat()
            elif token.type == Datatype.BOOL:
                return PyduinoBool()
            elif token.type == Datatype.STRING:
                return PyduinoString()
            elif token.type == Datatype.VOID:
                return PyduinoVoid()
        else:
            if PyduinoArray.is_typename(tokens):
                return PyduinoArray.is_typename(tokens)
        return False

    def copy(self) -> 'PyduinoType':
        # TODO returns type without name
        return type(self)(self.name)


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
    C_TYPENAME = "void"
    @staticmethod
    def check_type(str: str):
        if str == "void":
            return PyduinoVoid()
        return False

    def __str__(self):
        return "void"


class PyduinoBool(PyduinoType):
    C_TYPENAME = "bool"
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
        return True, PyduinoString(f"std::to_string({self.name})")

    def to_int(self):
        return True, PyduinoInt(f"({self.name} ? 1 : 0)")

    def to_float(self):
        return True, PyduinoFloat(f"({self.name} ? 1.0 : 0.0)")

    def to_bool(self):
        return True, self.copy()

    @staticmethod
    def check_type(string: str) -> 'PyduinoType':
        if string == "True" or string == "False":
            return PyduinoBool(string.lower())
        return False

    def __str__(self):
        return "bool"


class PyduinoInt(PyduinoType):
    SIZE_BYTES = 4
    ARDUINO_BYTE_CONVERSION = "bytesToInt"
    C_TYPENAME = "py_int"

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

    def plus_plus(self):
        return True, PyduinoInt(f"{self.name}++")

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
    def bytes_to_type(buffer_name: str):
        return True, PyduinoInt(f"(*static_cast<py_int*>(static_cast<void*>({buffer_name})))")

    def type_to_bytes(self):
        return True, f"static_cast<char*>(static_cast<void*>(&{self.name}))"

    @staticmethod
    def check_type(str: str):
        if str.isdigit():
            return PyduinoInt(str)
        return False

    def __str__(self):
        return "int"


class PyduinoFloat(PyduinoType):
    SIZE_BYTES = 4
    ARDUINO_BYTE_CONVERSION = "bytesToFloat"
    C_TYPENAME = "float"

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

    def plus_plus(self):
        return True, PyduinoFloat(f"{self.name}++")

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
    def bytes_to_type(buffer: str) -> 'tuple[bool, str | PyduinoType]':
        return True, PyduinoFloat(f"(*static_cast<float*>(static_cast<void*>({buffer})))")

    def type_to_bytes(self) -> 'tuple[bool, str]':
        return True, f"static_cast<char*>(static_cast<void*>(&{self.name}))"


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
    ARDUINO_BYTE_CONVERSION = "bytesToString"
    C_TYPENAME = "string"
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
        if not index.is_type(PyduinoInt()):
            return False, f"Cannot index array with {index}"
        item = self.item.copy()
        item.name = f"{self.name}[{index.name}]"
        return True, item

    @staticmethod
    def check_type(value: Token, transpiler: 'Transpiler'):
        # TODO add error messages
        if value.type != Brackets.SQUARE:
            return False

        if not value.inside:
            return PyduinoArray(PyduinoAny())

        items = []
        last_comma = 0
        for i in range(len(value.inside)):
            if value.inside[i].type == Separator.COMMA:
                items.append(value.inside[last_comma:i])
                last_comma = i + 1
        items.append(value.inside[last_comma:])

        items = [Value.do_value(item, transpiler) for item in items]

        if False in items:
            return False

        for i in range(len(items)):
            if not items[i].type.is_type(items[0].type):
                transpiler.data.newError(f"Cannot mix types in array", items[i].location)

        return PyduinoArray(items[0].type, size=len(items), name=f"{{{','.join([item.name for item in items])}}}")

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
        dimensions = [self.size]
        if self.item.is_iterable():
            dimensions += self.item.dimensions()
        return dimensions

    def set_dimensions(self, dimensions: list[int]):
        self.size = dimensions[0]
        if self.item.is_iterable():
            self.item.set_dimensions(dimensions[1:])

    @staticmethod
    def is_typename(tokens: list[Token]) -> 'PyduinoType':
        if PyduinoType.get_type_from_token([tokens[0]]):
            if all(t.type == Brackets.SQUARE for t in tokens[1:]):
                if all(not t.inside for t in tokens[1:]):
                    return PyduinoArray(PyduinoType.get_type_from_token(tokens[:-1]))
        return False

    def __str__(self):
        return f"{self.item}[]"

    def copy(self) -> 'PyduinoArray':
        return PyduinoArray(self.item.copy())


Types = {"int": PyduinoInt, "float": PyduinoFloat, "str": PyduinoString}


class Value:

    def __init__(self, name: str, type: PyduinoType, location: 'Range'):
        self.name = name
        self.type = type.copy()
        self.type.name = name
        self.location = location
        self.current_reference: Range = None

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
                            values[i] = Constant(t.name, t, Range.fromPositions(values[i - 1].location.start,
                                                                                values[i].location.end))
                            del values[i - 1]
                            shift_left += 1
                        else:
                            transpiler.data.newError(t, transpiler.location.range)
                            transpiler.data.invalid_line_fallback()
            shift_left = 0

            for i in range(1, len(values) - 1):
                i -= shift_left
                if values[i].type in o:
                    possible, t = values[i - 1].type.operator(values[i].type.code, values[i + 1].type)
                    if possible:
                        values[i - 1] = Constant(t.name, t, Range.fromPositions(values[i - 1].location.start,
                                                                                values[i + 1].location.end))
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

            t = PyduinoType.check_type(v, transpiler)
            if t:
                return Constant(t.name, t, v.location)

            elif v.type == Brackets.ROUND:
                return Value.do_value(v.inside, transpiler)


        else:
            # check function call
            from server.transpiler.function import Function
            var = Function.check_call(value, transpiler)
            if var:
                if var is True:
                    transpiler.data.newError(f"Function returning void cannot be used as value",
                                             Range.fromPositions(value[0].location.start, value[-1].location.end))
                    raise InvalidLineError(transpiler.location.range)
                return var

            # check if it is a getitem
            if value[0].type == Word.IDENTIFIER:
                if all([v.type == Brackets.SQUARE for v in value[1:]]):
                    # it is a getitem
                    var = transpiler.scope.get_Variable(value[0].value, value[0].location.start)
                    indices = [Value.do_value(b.inside, transpiler) for b in value[1:]]
                    if var:
                        for i in range(len(indices) - 1, -1, -1):
                            possible, var = var.type.get_item(indices[i].type)
                            if not possible:
                                transpiler.data.newError(var, value[i].location)
                                break
                            var = Constant(var.name, var,
                                           Range.fromPositions(value[0].location.start, value[-1].location.end))
                        return var
                    else:
                        transpiler.data.newError(f"Variable {value[0].value} not defined", value[0].location)
                        transpiler.data.invalid_line_fallback.fallback(transpiler)

        transpiler.data.newError(f"Invalid value {value[0].value}", value[0].location)
        transpiler.data.invalid_line_fallback.fallback(transpiler)


class Constant(Value):
    pass


class Variable(Value):
    @staticmethod
    def check_definition(instruction: list[Token], transpiler: 'Transpiler') -> bool:
        instruction_types = [i.type for i in instruction]
        if Separator.ASSIGN not in instruction_types:
            return False

        left = instruction[:instruction_types.index(Separator.ASSIGN)]
        value = instruction[instruction_types.index(Separator.ASSIGN) + 1:]
        if len(left) < 2:
            transpiler.data.newError(f"Invalid variable definition",
                                     Range.fromPositions(instruction[0].location.start, instruction[-1].location.end))
            return True

        if left[-1].type != Word.IDENTIFIER:
            transpiler.data.newError(f"{left[-1].value} is not a valid variable name", left[-1].location)
            return True

        datatype_tkns = left[:-1]
        name = left[-1]
        datatype = PyduinoType.get_type_from_token(datatype_tkns)

        if not datatype:
            transpiler.data.newError(f"Invalid datatype {''.join([str(d.value) for d in datatype_tkns])}",
                                     Range.fromPositions(datatype_tkns[0].location.start,
                                                         datatype_tkns[-1].location.end))
            return True

        value = Value.do_value(value, transpiler)
        c_value = value.type.name

        variable = Variable(name.value, value.type, value.location)
        value.type.name = name.value

        if transpiler.scope.get_Variable(name.value, variable.location.start):
            transpiler.data.newError(f"Variable '{name}' is already defined", variable.location)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        if not datatype.is_type(value.type):
            transpiler.data.newError(f"Cannot convert {value.type} to {datatype}", variable.location)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        if value.type.is_iterable():
            base_type = str(datatype).split("[")[0]
            c_code = f"{base_type} {name.value}{''.join(f'[]' for i in value.type.dimensions())} = {c_value};"
            variable.type.set_dimensions(value.type.dimensions())

        else:
            c_code = f"{variable.type.C_TYPENAME} {name.value} = {c_value};"

        transpiler.scope.add_Variable(variable, variable.location.start)
        transpiler.data.code_done.append(c_code)
        return True

    @staticmethod
    def check_assignment(instruction: list[Token], transpiler: 'Transpiler') -> bool:
        instruction_types = [i.type for i in instruction]

        if len(instruction_types) >= 3 and instruction_types[0] == Word.IDENTIFIER and instruction_types[1] == Math_Operator.PLUS and instruction_types[2] == Math_Operator.PLUS:
            if len(instruction) > 3:
                transpiler.data.newError(f"No Code should be after ++", Range.fromPositions(instruction[2].location.start, instruction[-1].location.end))

            variable = transpiler.scope.get_Variable(instruction[0].value, instruction[0].location.start)
            if variable:
                possible, var = variable.type.plus_plus()
                if not possible:
                    transpiler.data.newError(var, instruction[0].location)
                    return True
                transpiler.data.code_done.append(f"{var.name};")
                return True
            else:
                transpiler.data.newError(f"Variable {instruction[0].value} not defined", instruction[0].location)
                return True

        if not Separator.ASSIGN in instruction_types:
            return False


        left = instruction[:instruction_types.index(Separator.ASSIGN)]
        value = instruction[instruction_types.index(Separator.ASSIGN) + 1:]
        if len(left) != 1:
            if any([x.type != Brackets.SQUARE for x in left[1:]]):
                return False

            if left[0].type != Word.IDENTIFIER:
                transpiler.data.newError(f"{left[0].value} is not a valid variable name", left[0].location)

            # it is a getitem
            indices = [Value.do_value(b.inside, transpiler) for b in left[1:]]
            for i in indices:
                if not i:
                    transpiler.data.newError(f"Invalid index", i.location)

            var = transpiler.scope.get_Variable(left[0].value, left[0].location.start)
            if not var:
                transpiler.data.newError(f"Variable '{left[0].value}' is not defined", left[0].location)
                transpiler.data.invalid_line_fallback.fallback(transpiler)
                return True

            for i in indices:
                possible, new_var = var.type.get_item(i.type)
                if not possible:
                    transpiler.data.newError(new_var, i.location)
                    transpiler.data.invalid_line_fallback.fallback(transpiler)
                    return True
                var = Variable(var.name, new_var, var.location)

            value = Value.do_value(value, transpiler)

            if not var.type.is_type(value.type):
                transpiler.data.newError(f"Cannot convert {value.type} to {var.type}", value.location)
                transpiler.data.invalid_line_fallback.fallback(transpiler)
                return True

            if value.type.is_iterable():
                transpiler.data.newError(f"Cannot assign to iterable", var.location)
                return True

            transpiler.data.code_done.append(
                f"{var.name}{''.join(f'[{i.type.name}]' for i in indices)} = {value.type.name};")
            return True

        if left[0].type != Word.IDENTIFIER:
            transpiler.data.newError(f"{left[0].value} is not a valid variable name", left[0].location)

        variable = transpiler.scope.get_Variable(left[0].value, left[0].location.start)
        if not variable:
            transpiler.data.newError(f"Variable '{left[0].value}' is not defined", left[0].location)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        value = Value.do_value(value, transpiler)
        c_value = value.type.name

        if not variable.type.is_type(value.type):
            transpiler.data.newError(f"Cannot convert {value.type} to {variable.type}", value.location)
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True

        if value.type.is_iterable():
            transpiler.data.newError(f"Cannot assign to iterable", variable.location)
            return True

        transpiler.data.code_done.append(f"{variable.name} = {c_value};")
        return True

    def __bool__(self):
        return True
