from pyduino_utils import *
from scope import Scope
from control import Control

class Transpiler:
    def __init__(self, code:list[str], mode='main', line_offset=0):
        """
        :param code: The Code to transpile (including the #main or #board)
        :param mode: main or board
        :param line_offset: The line offset of the code segment
        """
        self.data:Data = Data(code,line_offset)
        self.location:CurrentLocation = CurrentLocation(code,self.data.indentations,line_offset,Range_ThrowError)

        self.utils = StringUtils(self.location,self.data, self)

        self.data.indentations = self.utils.getIndentations(self.data.code)

        self.scope = Scope(self.data)


    def next_line(self):
        index, line = next(self.data.enumerator)
        self.location.next_line()
        self.do_line(line)

    def transpileTo(self, line:int):
        """
        Transpiles up to the given line
        """
        while self.location.line < line:
            try:
                self.next_line()
            except StopIteration:
                # The end of the code is reached
                break
            except InvalidLineError:
                # The line is invalid, so it is skipped
                pass

    def do_line(self, line:str):
        instruction = line.strip()


