from pyduino_utils import *


class Control:
    @staticmethod
    def check(instuction:str,transpiler:'Transpiler'):
        """
        :param line:
        :param transpiler:
        :return: True if the line is a control statement, False if not
        """
        location = transpiler.location
        data = transpiler.data
        if instuction.startswith("if "):
            Control.do_if(instuction,data,location)
            return True

    @staticmethod
    def do_if(instruction:str,data:'Data',location:'CurrentLocation'):
        """
        :param instruction: The instruction to transpile
        :param data: The data object
        :param location: The location object
        """
        pass
