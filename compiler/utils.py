from constants import *
import variables
from functions import *


def do_variable_definition(line):
    """
    :param line: The complete line of the variable definition
    :return: The definition converted to C++
    """
    line = line.strip()
    datatype = line.split("=")[0].strip().split(" ")[0].strip()
    if datatype in PRIMITIVE_TYPES:
        name = line.split("=")[0].strip().split(" ")[1].strip()
        value = line.split("=")[1].strip()
        value, dt = do_value(value)
        if dt != datatype and dt is not None:
            raise SyntaxError(f"Datatype of {name} at line {variables.currentLineIndex} is not {datatype}")
        if variable_in_scope(name, variables.currentLineIndex):
            raise SyntaxError(f"Variable {name} at line {variables.currentLineIndex} already defined")
        add_variable_to_scope(name, datatype, variables.currentLineIndex)
        return f"{datatype} {name} = {value};"
    else:
        raise SyntaxError(f"Datatype {datatype} at line {variables.currentLineIndex} is not defined")


def do_variable_assignment(line):
    """
    :param line: The complete line of the variable assignment
    :return: The assignment converted to C++
    """
    line = line.strip()
    name = line.split("=")[0].strip()
    value = line.split("=")[1].strip()
    value, dt = do_value(value)
    if not variable_in_scope(name, variables.currentLineIndex):
        raise SyntaxError(f"Variable {name} at line {variables.currentLineIndex} not defined")
    if dt != variable_in_scope(name, variables.currentLineIndex)[1] and dt is not None:
        raise SyntaxError(f"Datatype of {name} at line {variables.currentLineIndex} is not {dt}")
    return f"{name} = {value};"


def do_value(value) -> (str, str):
    if value[0] == '"' == value[-1]:
        return value, "string"
    value = value.strip()
    # remove double Whitespaces from value
    while "  " in value:
        value = value.replace("  ", " ")
    while "and" in value:
        value = value.replace("and", "&&")
    while "or" in value:
        value = value.replace("or", "||")
    while "not" in value:
        value = value.replace("not", "!")
    values = value.split(" ")
    for i in range(len(values)):
        splitlist = []
        last_index = 0
        for j in range(len(values[i])):
            if values[i][j] in ARITHMETIC_OPERATORS:
                splitlist.append(values[i][last_index:j])
                splitlist.append(values[i][j])
                last_index = j + 1
            elif values[i][j] in BRACKETS:
                splitlist.append(values[i][last_index:j])
                splitlist.append(values[i][j])
                last_index = j + 1
            elif values[i][j] in CONDITION_OPERATORS_LEN1:
                splitlist.append(values[i][last_index:j])
                splitlist.append(values[i][j])
                last_index = j + 1
            elif j + 1 < len(values[i]) and values[i][j:j + 2] in CONDITION_OPERATORS_LEN2:
                splitlist.append(values[i][last_index:j])
                splitlist.append(values[i][j:j + 2])
                last_index = j + 2
            elif values[i][j] == "!":
                splitlist.append(values[i][last_index:j])
                splitlist.append(values[i][j])
                last_index = j + 1

        splitlist.append(values[i][last_index:])
        values[i] = splitlist

    values = [i for j in values for i in j if i != ""]
    if len(values) > 1:
        datatypes = []
        for i in range(len(values)):
            if not values[i] in OPERATORS + BRACKETS:
                values[i], dt = do_value(values[i])
                datatypes.append(dt)
            else:
                datatypes.append(None)
        # TODO check if datatypes are correct
        return " ".join(values), datatypes[0]
    if value[0] in NUMBERS:
        for i in range(len(value)):
            if value[i] not in NUMBERS and value[i] != ".":
                break
        else:
            if "." in value:
                return value, "float"
            else:
                return value, "int"
        raise SyntaxError(f"Value {value} at line {variables.currentLineIndex} is not a number")

    elif value[0] == '"':
        if value[-1] == '"':
            return value, "string"
        raise SyntaxError(f"Value {value} at line {variables.currentLineIndex} is not a string")
    elif value[0] == "'":
        if value[2] == "'" and len(value) == 3:
            return value, "char"
        raise SyntaxError(f"Value {value} at line {variables.currentLineIndex} is not a character")

    elif value[0] == "[":
        raise NotImplementedError("Lists are not implemented yet")

    elif value[0] == "{":
        raise NotImplementedError("Dictionaries are not implemented yet")

    elif value[0] == "(":
        raise NotImplementedError("Tuples are not implemented yet")

    elif value[0] == "T" and value[1] == "r" and value[2] == "u" and value[3] == "e" and len(value) == 4:
        return "true", "bool"

    elif value[0] == "F" and value[1] == "a" and value[2] == "l" and value[3] == "s" and value[4] == "e" and len(
            value) == 5:
        return "false", "bool"

    elif value[0] == "n" and value[1] == "o" and value[2] == "n" and value[3] == "e" and len(value) == 4:
        return "nullptr", "none"

    elif (s := variable_in_scope(value, variables.currentLineIndex)) is not None:
        return value, s[1]

    elif (f := check_function_execution(value, variables.currentLineIndex)) is not None and f[2]:
        return f[0], f[1]
    else:
        raise SyntaxError(f"Value '{value}' at line {variables.currentLineIndex} is not defined")


def do_arguments(argstring):
    """
    :param argstring: all arguments as a string WITHOUT the brackets
    :return: argument list, kwarg dictionary
    """
    args = []  # Format: (name, datatype)
    kwargs = {}
    all_args = argstring.split(",")
    for arg in all_args:
        arg = arg.strip()
        if "=" not in arg:
            if kwargs:
                raise SyntaxError(f"Positional (=normal) argument after keyword argument at line {variables.currentLineIndex}")
            args.append(do_value(arg))
        else:
            name, value = arg.split("=")
            name = name.strip()
            value = value.strip()
            kwargs[name] = do_value(value)
    return args, kwargs


def add_variable_to_scope(name, datatype, line_index):
    for start, end in variables.scope.keys():
        if start <= line_index <= end:
            variables.scope[(start, end)][0].append((name, datatype))
            return


def variable_in_scope(name, line_index):
    """
    :return: (name, datatype) if variable is in scope, else None
    """
    for start, end in variables.scope.keys():
        if start <= line_index <= end:
            for i in variables.scope[(start, end)][0]:
                if i[0] == name:
                    return i


def next_sys_variable():
    global sysVariableIndex
    sysVariableIndex += 1
    return f"__sys_var_{324987 * sysVariableIndex}"
