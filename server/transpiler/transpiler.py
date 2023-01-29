from pyduino_utils import *

class Transpiler:
    def __init__(self, code, mode='main', line_offset=0):
        """
        :param code: The Code to transpile (including the #main or #board)
        :param mode: main or board
        :param line_offset: The line offset of the code segment
        """
        self.data:Data = Data(code,line_offset)
        self.location:CurrentLocation = CurrentLocation(code,self.data.indentations,line_offset,Range_ThrowError)

        self.utils = StringUtils(self.location,self.data)

        self.data.indentations = self.utils.getIndentations(self.data.code)


    def next_line(self):
        index, line = next(self.data.enumerator)
        self.location.next_line()


