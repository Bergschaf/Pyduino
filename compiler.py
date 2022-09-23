FILENAME = "testPyduino.pino"

DEFAULT_INDEX_LEVEL = 4  # spaces

CLOSING_BRACKETS = {"(": ")", "[": "]", "{": "}"}
BRACKETS = ["(", ")", "[", "]", "{", "}"]

PRIMITIVE_TYPES = ["int", "float", "char", "bool"]

NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

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
scopes = {}  # variables Format: key: (beginning_row,end_row) value: list of variables: variable: (name, datatype)


# functions


def do_line(index, line):
    pass


def do_arguments(start_row_index, start_col_index, end_row_index, end_col_index):
    pass


def in_scope(line_index, name):
    """Returns the Variable with the name if it is in the current scope"""
    for scope in scopes:
        if scope[0] <= line_index <= scope[1]:
            for variable in scopes[scope]:
                if variable.name == name:
                    return variable
    return None


def add_to_scope(line_index, variable):
    for scope in scopes:
        if scope[0] <= line_index <= scope[1]:
            scopes[scope].append(variable)
            return


def do_variable(l: str, line_index: int):
    l = l.lstrip()
    datatype = l.split(" ")[0]
    if datatype in PRIMITIVE_TYPES:
        name = l.split(" ")[1]
        if in_scope(line_index, name) is None:
            add_to_scope(line_index, (name, datatype))
            try:
                value = l.split("=")[1]
            except IndexError:
                raise SyntaxError(f"Variable '{name}' has no value at line {line_index}")
            done_value, dt = do_value(value)
            if dt == "int":
                return f"{datatype} {name}={done_value};"
            else:
                raise SyntaxError(
                    f"Wrong Data Type at line {line_index}. Variable of type '{datatype}' can't be assigned to a value of type '{dt}'")
        else:
            raise SyntaxError(f"Variable '{name}' already exists in current scope")
    else:
        raise NotImplementedError(f"Datatype '{datatype}' might not be implemented yet")


def do_value(value, line_index) -> (str, str):
    value = value.strip()
    if value[0] in NUMBERS:
        for i in range(len(value)):
            if value[i] not in NUMBERS and value[i] != ".":
                break
        else:
            if "." in value:
                return value, "float"
            else:
                return value, "int"
        raise SyntaxError(f"Value {value} at line {line_index} is not a number")

    elif value[0] == '"':
        if value[-1] == '"':
            return value, "string"
        raise SyntaxError(f"Value {value} at line {line_index} is not a string")
    elif value[0] == "'":
        if value[2] == "'" and len(value) == 3:
            return value, "char"
        raise SyntaxError(f"Value {value} at line {line_index} is not a char")

    elif value[0] == "[":
        raise NotImplementedError("Lists are not implemented yet")

    elif value[0] == "{":
        raise NotImplementedError("Dictionaries are not implemented yet")

    elif value[0] == "(":
        raise NotImplementedError("Tuples are not implemented yet")

    elif value[0] == "T" and value[1] == "r" and value[2] == "u" and value[3] == "e" and len(value) == 4:
        return "true", "bool"

    elif value[0] == "F" and value[1] == "a" and value[2] == "l" and value[3] == "s" and value[4] == "e" and len(value) == 5:
        return "false", "bool"

    elif value[0] == "n" and value[1] == "o" and value[2] == "n" and value[3] == "e" and len(value) == 4:
        return "nullptr", "none"

    elif (scope := in_scope(line_index, value)) is not None:
        return value, scope[1]

    else:
        raise SyntaxError(f"Value {value} at line {line_index} is not valid")




def do_print(line, row_index):
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
