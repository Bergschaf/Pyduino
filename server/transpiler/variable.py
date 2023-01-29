from pyduino_types import *
from value import Value

class Variable:
    def __init__(self, name: str, type: type[PyduinoType]):
        self.name = name
        self.type = type

    @staticmethod
    def check_definition(instruction: str, line: int, transpiler: 'Transpiler') -> bool:
        range = Range(line, 0, complete_line=True, data=transpiler.data)
        operator_location = transpiler.utils.searchOutsideBrackets("=", range=range,fallback=StringNotFound_DoNothing)
        if not operator_location:
            return False

        split = instruction.split("=")
        left = split[0].strip().split(" ")
        if len(left) != 2:
            transpiler.data.newError(f"Invalid variable definition", range)
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

        if datatype not in Types.keys():
            transpiler.data.newError(f"Unknown type '{datatype}'", transpiler.location.getRangeFromString(datatype))
            transpiler.data.invalid_line_fallback.fallback(transpiler)
            return True






