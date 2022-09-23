FILENAME = "testPyduino.pino"

DEFAULT_INDEX_LEVEL = 4  # spaces

CLOSING_BRACKETS = {"(": ")", "[": "]", "{": "}"}
BRACKETS = ["(", ")", "[", "]", "{", "}"]

PRIMITIVE_TYPES = ["int", "float", "char", "bool"]

code_pc = None
code_board = None
with open("testPyduino.pino", "r") as f:
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
scopes = {} # variables

# functions



def do_line(index, line):
    pass

def do_arguments(start_row_index, start_col_index, end_row_index, end_col_index):
    pass

def do_variable(line):
    pass

def do_value(value):
    pass

def do_print(line,row_index):
    col_index = line.find("print") + 5
    if line[col_index] == "(":
        row, col = find_closing_bracket("(", row_index, col_index)

    else:
        raise SyntaxError(f"Expected '(' at line {index} col {index} after 'print' statement")


def find_closing_bracket(bracket, start_row, start_col):
    closing_bracket = CLOSING_BRACKETS[bracket]
    bracket_level_1 = 0
    bracket_level_2 = 0
    bracket_level_3 = 0
    if bracket == "(":
        bracket_level_1 = 1
    elif bracket == "[":
        bracket_level_2 = 1
    elif bracket == "{":
        bracket_level_3 = 1
    row = start_row
    col = start_col + 1
    while row < len(code):
        while col < len(code[row]):
            if code[row][col] == BRACKETS[0]:
                bracket_level_1 += 1
            elif code[row][col] == BRACKETS[1]:
                bracket_level_1 -= 1
            elif code[row][col] == BRACKETS[2]:
                bracket_level_2 += 1
            elif code[row][col] == BRACKETS[3]:
                bracket_level_2 -= 1
            elif code[row][col] == BRACKETS[4]:
                bracket_level_3 += 1
            elif code[row][col] == BRACKETS[5]:
                bracket_level_3 -= 1
            if code[row][
                col] == closing_bracket and bracket_level_1 == 0 and bracket_level_2 == 0 and bracket_level_3 == 0:
                return row, col
            col += 1
        row += 1
    raise SyntaxError(f"No closing bracket found for '{bracket}' at line {start_row} col {start_col}")


main_it = enumerate(code_pc)
for index, line in enumerate(code_pc):
    pass
# main end
main_cpp += ["return 0;", "}"]
with open(FILENAME[:-5] + ".cpp", "w") as f:
    f.write("\n".join(main_cpp))

do_print(1, "print(1)")
# print(code)
# print(code_pc)
# print(code_board)
