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
        if type(tokens[0].type) is Datatype:
            if all(t.type == Brackets.SQUARE for t in tokens):
                if all(not t.inside for t in tokens):
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
        self.type = type
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
                        return Constant(var.name, var,
                                        Range.fromPositions(value[0].location.start, value[-1].location.end))

        transpiler.data.newError(f"Invalid value {value[0].value}", value[0].location)
        transpiler.data.invalid_line_fallback.fallback(transpiler)


class Constant(Value):
    pass


class Variable(Value):
    @staticmethod
    def check_definition(instruction: list[Token], transpiler: 'Transpiler') -> bool:
        # line = transpiler.location.position.line
        # instruction_range = Range(line, 0, complete_line=True, data=transpiler.data)
        # operator_location = transpiler.utils.searchOutsideBrackets("=", range=instruction_range,
        #                                                           fallback=StringNotFound_DoNothing)
        instruction_types = [i.type for i in instruction]
        if Separator.ASSIGN not in instruction_types:
            return False

        left = instruction[:instruction_types.index(Separator.ASSIGN)]
        value = instruction[instruction_types.index(Separator.ASSIGN) + 1:]
        if len(left) < 2:
            transpiler.data.newError(f"Invalid variable definition",
                                     Range.fromPositions(instruction[0].location.start, instruction[-1].location.end))
            return True

        if left[1].type != Word.IDENTIFIER:
            transpiler.data.newError(f"{left[1].value} is not a valid variable name", left[1].location)
            return True

        datatype_tkns = left[:-1]
        name = left[-1]
        datatype = PyduinoType.get_type_from_token(datatype_tkns)

        if not datatype:
            transpiler.data.newError(f"Invalid datatype {''.join([str(d.value) for d in datatype_tkns])}", Range.fromPositions(datatype_tkns[0].location.start, datatype_tkns[-1].location.end))
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
            c_code = f"{base_type} {name.value}{''.join(f'[{i}]' for i in value.type.dimensions())} = {c_value};"
            variable.type.set_dimensions(value.type.dimensions())

        else:
            c_code = f"{datatype} {name.value} = {c_value};"

        transpiler.scope.add_Variable(variable, variable.location.start)
        transpiler.data.code_done.append(c_code)
        return True
