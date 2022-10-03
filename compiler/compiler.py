from utils import *
from constants import *

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


# functions

def do_line(row_index, l):
    instruction = l.strip()
    if instruction[0] == "#":
        return
    elif any([instruction.startswith(i) for i in PRIMITIVE_TYPES]):
        return do_variable(instruction, row_index)
    elif instruction[:5] == "print":
        return do_print(row_index, instruction[5:])
    elif instruction[:2] == "if":
        return do_if(row_index, instruction)
    elif instruction[:5] == "while":
        return do_while(row_index, instruction)
    elif instruction[:3] == "for":
        return do_for(row_index, instruction)
    # TODO: das am ende
    elif "=" in instruction:
        return do_assignment(row_index, instruction)
    # TODO ggf fix
    elif "++" in instruction:
        return instruction + ";"








main_it = enumerate(code_pc)
print("\n\n------\n")
for IteratorLineIndex, line in main_it:
    main_cpp.append(do_line(IteratorLineIndex, line))
# main end
main_cpp += ["return 0;", "}"]
with open(FILENAME[:-5] + ".cpp", "w") as f:
    f.write("\n".join(main_cpp))

# print(code)
# print(code_pc)
# print(code_board)
