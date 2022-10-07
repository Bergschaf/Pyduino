from utils import *
from constants import *
from intitializer import intialize

Variables = []

IteratorLineIndex = 0
SysVariableIndex = 0

code_pc = None
code_board = None
with open("../testPyduino.pino", "r") as f:
    code = [l.strip("\n").rstrip() for l in f.readlines() if l.strip("\n").replace(" ", "") != ""]
    if code[0] == "#main":
        for i in range(len(code)):
            if code[i] == "#board":
                code_pc = code[1:i]
                code_board = code[i + 1:]
                break
        else:
            code_pc = code[1:]
    elif code[0] == "#board":
        code_board = code[1:]
    else:
        raise SyntaxError("No start defined, it should be '#board' or '#main' at the beginning")

# main code
print("\n\n------\n")
intialize(code_pc)
for variables.currentLineIndex, line in variables.iterator:
    variables.code_done.append(do_line(line))

variables.code_done.append("}")
if (variables.arduino_needed == True):
    variables.code_done.insert(0, '#include "SerialCommunication/SerialPc.cpp"')
    variables.code_done.insert(4, "Arduino arduino = Arduino();")
print(variables.code_done)
with open(FILENAME[:-5] + ".cpp", "w") as f:
    f.write("\n".join(variables.code_done))
