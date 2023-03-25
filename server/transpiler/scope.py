from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.transpiler.variable import Variable
    from server.transpiler.function import Function

from server.transpiler.pyduino_utils import *


class Scope:
    def __init__(self, transpiler: Transpiler):
        self.transpiler = transpiler
        self.functions = []


    def get_Variable(self, name: str) -> 'Variable':
        indent = self.transpiler.current_indent
        while indent.level > 0:
            for i in indent.variables:
                if i.name == name:
                    return i
            indent = indent.parent
        return False

    def get_Function(self, name: str, position: Position) -> 'Function':
        for i in self.functions:
            if i.name == name:
                if position.is_bigger(i.position):
                    return i
        return False

    def add_Variable(self, variable: 'Variable'):
        self.transpiler.current_indent.variables.append(variable)

    def add_Function(self, function: 'Function', position: 'Position'):
        function.position = position
        self.functions.append(function)

    def add_functions(self, functions: list['Function']):
        for f in functions:
            f.position = Position(0, 0)
        self.functions.extend(functions)
