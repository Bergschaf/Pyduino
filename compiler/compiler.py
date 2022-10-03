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


def do_arguments(start_row_index, start_col_index, end_row_index, end_col_index):
    args = []  # Format: (name, datatype)
    kwargs = {}
    if start_row_index == end_row_index:
        argstring = code_pc[start_row_index][start_col_index:end_col_index]
    else:
        argstring = code_pc[start_row_index:end_row_index]
        argstring[0] = argstring[0][start_col_index:]
        argstring[-1] = argstring[-1][:end_col_index]
    argstring = "".join(argstring)
    all_args = argstring.split(",")
    for arg in all_args:
        arg = arg.strip()
        if "=" not in arg:
            if kwargs:
                raise SyntaxError(f"Positional argument after keyword argument at line {start_row_index}")
            args.append(do_value(arg, start_row_index))
        else:
            name, value = arg.split("=")
            name = name.strip()
            value = value.strip()
            kwargs[name] = do_value(value, start_row_index)
    return args, kwargs


def in_scope(line_index, name):
    """Returns the Variable with the name if it is in the current scope"""
    for scope in scopes.keys():
        if scope[0] <= line_index <= scope[1]:
            for variable in scopes[scope]:
                if variable[0] == name:
                    return variable
    return None


def add_to_scope(line_index, variable):
    """Fix this"""
    for scope in scopes:
        if scope[0] <= line_index <= scope[1]:
            scopes[scope].append(variable)
            return


def get_indentation_level(row_index):
    return (len(code_pc[row_index]) - len(code_pc[row_index].lstrip())) / 4


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
            done_value, dt = do_value(value, line_index)
            if dt == datatype:
                return f"{datatype} {name}={done_value};"
            else:
                return f"{datatype} {name}={done_value};"
            # else:
            #    raise SyntaxError(
            #        f"Wrong Data Type at line {line_index}. Variable of type '{datatype}' can't be assigned to a value of type '{dt}'")
        else:
            raise SyntaxError(f"Variable '{name}' already exists in current scope")
    else:
        raise NotImplementedError(f"Datatype '{datatype}' might not be implemented yet")




def do_print(row_index, line):
    col_index = code_pc[row_index].index("print") + 5
    newline = "<< endl"
    if line[0] == "(":
        row, col = find_closing_bracket("(", row_index, col_index)
        args, kwargs = do_arguments(row_index, col_index + 1, row, col)
        # if "newline" in kwargs.keys():
        #    print(kwargs["newline"])
        #    if kwargs["newline"] == "false":
        #        newline = ""
        #    if len(kwargs.keys()) > 1:
        #        raise SyntaxError(f"Unexpected keyword argument(s) at line {row_index}")
        # elif len(kwargs.keys()) > 0:
        #    raise SyntaxError(f"Unexpected keyword argument(s) at line {row_index}")
        return f"cout << {f'<< {WHITESPACE} <<'.join([a[0] for a in args])} {newline};"
    else:
        raise SyntaxError(f"Expected '(' at line {row_index} col {col_index} after 'print' statement")


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
    while row < len(code_pc):
        while col < len(code_pc[row]):
            if code_pc[row][col] == BRACKETS[0]:
                bracket_level_1 += 1
            elif code_pc[row][col] == BRACKETS[1]:
                bracket_level_1 -= 1
            elif code_pc[row][col] == BRACKETS[2]:
                bracket_level_2 += 1
            elif code_pc[row][col] == BRACKETS[3]:
                bracket_level_2 -= 1
            elif code_pc[row][col] == BRACKETS[4]:
                bracket_level_3 += 1
            elif code_pc[row][col] == BRACKETS[5]:
                bracket_level_3 -= 1
            if code_pc[row][
                col] == closing_bracket and bracket_level_1 == 0 and bracket_level_2 == 0 and bracket_level_3 == 0:
                return row, col
            col += 1
        row += 1
    raise SyntaxError(f"No closing bracket found for '{bracket}' at line {start_row} col {start_col}")


def do_if(row_index, line):
    global IteratorLineIndex
    col_index = line.index("if") + 2
    if line.strip()[-1] == ":":
        row = row_index
        col = len(line) - 1
        condition = do_value(line[col_index + 1:col], row_index)[0]
        print(condition, row_index)
        if get_indentation_level(row_index) + 1 != get_indentation_level(row + 1):
            raise SyntaxError(f"Expected indentation at line {row + 1}, (indentation = 4 Spaces)")
        for i in range(row + 1, len(code_pc)):
            if get_indentation_level(i) <= get_indentation_level(row_index):
                end_indentation_index = i - 1
                break
        else:
            end_indentation_index = len(code_pc) - 1
        print(condition, row_index, end_indentation_index)
        current_indentation_level = get_indentation_level(row_index)
        if_code = [f"if ({condition}) {{"]
        while IteratorLineIndex < end_indentation_index:
            identation_levels[i] = current_indentation_level + 1
            IteratorLineIndex, y = next(main_it)
            if_code.append(do_line(IteratorLineIndex, y))
        if_code.append("}")
        return "\n".join(if_code)
    else:
        raise SyntaxError(f"Expected ':' at line {row_index} col {col_index}")


def do_while(row_index, line):
    global IteratorLineIndex
    col_index = line.index("while") + 5
    if line.strip()[-1] == ":":
        row = row_index
        col = len(line) - 1
        condition = do_value(line[col_index + 1:col], row_index)[0]
        if get_indentation_level(row_index) + 1 != get_indentation_level(row + 1):
            raise SyntaxError(f"Expected indentation at line {row + 1}, (indentation = 4 Spaces)")
        for i in range(row + 1, len(code_pc)):
            if get_indentation_level(i) <= get_indentation_level(row_index):
                end_indentation_index = i - 1
                break
        else:
            end_indentation_index = len(code_pc) - 1
        current_indentation_level = get_indentation_level(row_index)
        print(end_indentation_index)
        while_code = [f"while ({condition}) {{"]
        while IteratorLineIndex < end_indentation_index:
            identation_levels[i] = current_indentation_level + 1
            IteratorLineIndex, y = next(main_it)
            while_code.append(do_line(IteratorLineIndex, y))
        while_code.append("}")
        return "\n".join(while_code)
    else:
        raise SyntaxError(f"Expected ':' at line {row_index} col {col_index}")


def do_for(row_index, line):
    global IteratorLineIndex
    col_index = line.index("for") + 3
    if line.strip()[-1] == ":":
        row = row_index
        col = len(line) - 1
        elements = [x.strip() for x in line[col_index + 1:-1].split("in")]

        if len(elements) != 2:
            raise SyntaxError(f"Expected 'in' at line {row_index} col {col_index}")
        counter_variable = elements[0]
        if get_indentation_level(row_index) + 1 != get_indentation_level(row + 1):
            raise SyntaxError(f"Expected indentation at line {row + 1}, (indentation = 4 Spaces)")
        for i in range(row + 1, len(code_pc)):
            if get_indentation_level(i) <= get_indentation_level(row_index):
                end_indentation_index = i - 1
                break
        else:
            end_indentation_index = len(code_pc) - 1
        current_indentation_level = get_indentation_level(row_index)
        if elements[1][:5] == "range":
            if elements[1][5] != "(":
                raise SyntaxError(f"Expected '(' at line {row_index} col {col_index}")
            end_col = find_closing_bracket("(", row_index, code_pc[row_index].index("range") + 6)
            range_arguments, range_kwargs = do_arguments(row_index, code_pc[row_index].index("range") + 6, row_index,
                                                         end_col[1])
            if any([x[1] != "int" for x in range_arguments]):
                raise SyntaxError(f"Expected type int as range argument in line {row_index}")
            if len(range_kwargs) != 0:
                raise SyntaxError(f"Unexpected keyword arguments in range function in line {row_index}")

            if len(range_arguments) == 1:
                for_code = [f"for (int {counter_variable} = 0; {counter_variable} < {range_arguments[0][0]} ; {counter_variable}++) {{"]
            elif len(range_arguments) == 2:
                for_code = [f"for (int {counter_variable} = {range_arguments[0][0]}; {counter_variable} < {range_arguments[1][0]} ; {counter_variable}++) {{"]
            elif len(range_arguments) == 3:
                for_code = [
                    f"for (int {counter_variable} = {range_arguments[0][0]}; {counter_variable} < {range_arguments[1][0]} ; {counter_variable} += {range_arguments[2][0]}) {{"]
            else:
                raise SyntaxError(f"Expected 1, 2 or 3 arguments in range() at line {row_index} col {col_index}")

        else:
            for_code = [f"for (int {(sys_var := next_sys_variable())} = 0; {sys_var} < {do_value(elements[1], row_index)[0]}.size(); {sys_var}++) {{",f"auto {counter_variable} = {do_value(elements[1], row_index)[0]}[{sys_var}];"]
        add_to_scope(row_index,(counter_variable, "auto"))
        while IteratorLineIndex < end_indentation_index:
            identation_levels[i] = current_indentation_level + 1
            IteratorLineIndex, y = next(main_it)
            for_code.append(do_line(IteratorLineIndex, y))
        for_code.append("}")
        return "\n".join(for_code)
    else:
        raise SyntaxError(f"Expected ':' at line {row_index} col {col_index}")




def next_sys_variable():
    global SysVariableIndex
    SysVariableIndex += 1
    return f"__sys_var_{324987 * SysVariableIndex}"

def do_assignment(row_index, line):
    variable, value = line.split("=")
    return f"{variable}={do_value(value, row_index)[0]};"




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
