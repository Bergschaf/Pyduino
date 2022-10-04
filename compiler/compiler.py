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
main_cpp = ["#include <iostream>", "using namespace std;", "int main() {"]
scopes = {(0,
           len(code_pc)): []}  # variables Format: key: (beginning_row,end_row) value: list of variables: variable: (name, datatype)
identation_levels = [0 for i in range(len(code_pc))]


print("\n\n------\n")
intialize(code_pc)
for variables.currentLineIndex, line in variables.iterator:
    do_line(line)
variables.code_done += ["return 0;", "}"]
with open(FILENAME[:-5] + ".cpp", "w") as f:
    f.write("\n".join(variables.code_done))

# print(code)
# print(code_pc)
# print(code_board)
