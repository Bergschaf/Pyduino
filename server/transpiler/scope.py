from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from variable import Variable
    from function import Function

from pyduino_utils import *


class Scope:
    def __init__(self, data):
        self.data = data

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
