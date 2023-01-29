from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from variable import Variable
    from function import Function

from pyduino_utils import *


class Scope:
    def __init__(self, data: Data, location: CurrentLocation):
        self.data = data
        self.location = location

        self.variables: dict[Range, list[Variable]]
        self.functions: dict[Range, list[Function]]

        self.variables = {Range(0, 0, end_line=len(self.data.indentations) - 1, complete_line=True, data=data): []}
        self.functions = {Range(0, 0, end_line=len(self.data.indentations) - 1, complete_line=True, data=data): []}

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
                self.functions[Range(start, 0, end_line=end, complete_line=True, data=data)] = []

    def get_Variable(self, name: str, position: Position, fallback: type[StringNotFound_Fallback]=StringNotFound_ErrorCompleteRange):
        for i in self.variables:
            if i.in_range(position):
                for j in self.variables[i]:
                    if j.name == name:
                        return j
        fallback.fallback(self.data, self.location.getFullWordRange(position, word=name),name,custom_message= f"Variable '{name}' is not defined in this scope")
        return False

    def get_Function(self, name: str, position: Position, fallback: type[StringNotFound_Fallback]=StringNotFound_ErrorCompleteRange):
        for i in self.functions:
            if i.in_range(position):
                for j in self.functions[i]:
                    if j.name == name:
                        return j
        fallback.fallback(self.data, self.location.getFullWordRange(position, word=name),name,custom_message= f"Function '{name}' is not defined in this scope")
        return False

    def add_Variable(self, variable: Variable, position: Position):
        for i in self.variables:
            if i.in_range(position):
                self.variables[i].append(variable)

    def add_Function(self, function: Function, position: Position):
        for i in self.functions:
            if i.in_range(position):
                self.functions[i].append(function)