from server.transpiler.variable import *


class Function:
    def __init__(self, name: str, return_type: PyduinoType, arguments: list[tuple[str, PyduinoType]]):
        self.name = name
        self.return_type = return_type
        self.arguments = arguments

    @staticmethod
    def checK_definition(instruction: str, transpiler: 'Transpiler'):
        return_type = instruction.split(' ', 1)

        if len(return_type) < 2:
            return False

        return_type, name = return_type[0], return_type[1]

        return_type = PyduinoType.check_type(return_type)

        if not return_type:
            return False

        name = StringUtils.check_colon(name, transpiler)



