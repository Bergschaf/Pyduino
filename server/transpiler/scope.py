from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.transpiler.variable import Variable
    from server.transpiler.function import Function

from server.transpiler.pyduino_utils import *


class Scope:
    def __init__(self, data: Data, location: CurrentLocation):
        self.data = data
        self.location = location

        self.variables: dict[Range, list[Variable]]
        self.functions: list[Function]

        self.variables = {Range(0, 0, end_line=len(self.data.indentations) - 1, complete_line=True, data=data): []}
        self.functions = []

        for i in range(1, len(self.data.indentations)):
            if self.data.indentations[i] == self.data.indentations[i - 1]:
                continue
            if self.data.indentations[i] > self.data.indentations[i - 1]:
                start = i
                for pos_j, j in enumerate(self.data.indentations[i:]):
                    if j < self.data.indentations[i]:
                        end = pos_j + i - 1
                        break
                else:
                    end = len(self.data.indentations) - 1
                self.variables[Range(start, 0, end_line=end, complete_line=True, data=data)] = []

    def get_Variable(self, name: str, position: Position) -> 'Variable':
        for i in self.variables:
            if i.in_range(position):
                for j in self.variables[i]:
                    if j.name == name:
                        return j
        return False

    def get_Function(self, name: str, position: Position) -> 'Function':
        for i in self.functions:
            if i.name == name:
                if position.is_bigger(i.position):
                    return i
        return False

    def add_Variable(self, variable: 'Variable', position: 'Position'):
        for i in self.variables:
            if i.in_range(position) and self.data.indentations[i.start.line] == self.data.indentations[position.line]:
                self.variables[i].append(variable)

    def add_Function(self, function: 'Function', position: 'Position'):
        function.position = position
        self.functions.append(function)

    def add_functions(self, functions: list['Function']):
        for f in functions:
            f.position = Position(0, 0)
        self.functions.extend(functions)