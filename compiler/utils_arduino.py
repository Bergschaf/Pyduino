from constants_arduino import *
import variables_arduino


def reset_sys_variable():
    variables_arduino.sysVariableIndex = 0


def next_sys_variable():
    variables_arduino.sysVariableIndex += 1
    return f"_sys_var_{324987 * variables_arduino.sysVariableIndex}"


def find_closing_bracket_in_value(value, bracket, start_col):
    """
    :param value: the value to search in
    :param bracket: the bracket to search for
    :param start_col: the column to start searching from
    """
    if value[start_col] != bracket:
        raise SyntaxError(f"Value does not start with '{bracket}'")
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
    col = start_col + 1
    while col < len(value):
        if value[col] == BRACKETS[0]:
            bracket_level_1 += 1
        elif value[col] == BRACKETS[1]:
            bracket_level_1 -= 1
        elif value[col] == BRACKETS[2]:
            bracket_level_2 += 1
        elif value[col] == BRACKETS[3]:
            bracket_level_2 -= 1
        elif value[col] == BRACKETS[4]:
            bracket_level_3 += 1
        elif value[col] == BRACKETS[5]:
            bracket_level_3 -= 1
        if value[col] == closing_bracket and bracket_level_1 == 0 and bracket_level_2 == 0 and bracket_level_3 == 0:
            return col
        col += 1
    raise SyntaxError(
        f"No closing bracket found for '{bracket}' at line {variables_arduino.currentLineIndex} col {start_col}")


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
    while row < len(variables_arduino.code):
        while col < len(variables_arduino.code[row]):
            if variables_arduino.code[row][col] == BRACKETS[0]:
                bracket_level_1 += 1
            elif variables_arduino.code[row][col] == BRACKETS[1]:
                bracket_level_1 -= 1
            elif variables_arduino.code[row][col] == BRACKETS[2]:
                bracket_level_2 += 1
            elif variables_arduino.code[row][col] == BRACKETS[3]:
                bracket_level_2 -= 1
            elif variables_arduino.code[row][col] == BRACKETS[4]:
                bracket_level_3 += 1
            elif variables_arduino.code[row][col] == BRACKETS[5]:
                bracket_level_3 -= 1
            if variables_arduino.code[row][
                col] == closing_bracket and bracket_level_1 == 0 and bracket_level_2 == 0 and bracket_level_3 == 0:
                return row, col
            col += 1
        row += 1
    raise SyntaxError(f"No closing bracket found for '{bracket}' at line {start_row} col {start_col}")


def do_arguments(argstring):
    """
    :param argstring: all arguments as a string WITHOUT the brackets
    :return: argument list, kwarg dictionary
    """
    args = []  # Format: (name, datatype)
    kwargs = {}
    all_args = []
    # split the args, but ignore commas in brackets
    last_split = 0
    closing_bracket = 0
    for i in range(len(argstring)):
        if closing_bracket > i:
            continue
        if argstring[i] == ",":
            all_args.append(argstring[last_split:i])
            last_split = i + 1
        elif argstring[i] in OPENING_BRACKETS:
            closing_bracket = find_closing_bracket_in_value(argstring, argstring[i], i)
    all_args.append(argstring[last_split:])
    for arg in all_args:
        arg = arg.strip()
        if "=" not in arg:
            if kwargs:
                raise SyntaxError(
                    f"Positional (=normal) argument after keyword argument at line {variables_arduino.currentLineIndex}")
            args.append(do_value(arg))
        else:
            name, value = arg.split("=")
            name = name.strip()
            value = value.strip()
            kwargs[name] = do_value(value)
    return args, kwargs


from functions_arduino import check_function_execution, check_function_definition


def do_line(line):
    instruction = line.strip()
    if instruction[0] == "#":
        return
    elif any([instruction.startswith(i) for i in PRIMITIVE_TYPES + PRIMITIVE_ARRAY_TYPES]):
        if (f := check_function_definition(instruction)) is not None:
            return f
        else:
            return do_variable_definition(instruction)
    elif (f := check_function_execution(instruction)) is not None:
        return f[0] + ";"
    elif instruction[:2] == "if":
        return do_if(instruction)
    elif instruction[:5] == "while":
        return do_while(instruction)
    elif instruction[:3] == "for":
        return do_for(instruction)
    # TODO: das am Ende
    elif "=" in instruction:
        return do_variable_assignment(instruction)
    # TODO ggf fix
    elif "++" in instruction:
        return instruction + ";"


def do_variable_definition(line):
    """
    :param line: The complete line of the variable definition
    :return: The definition converted to C++
    """
    print(line)
    line = line.strip()
    datatype = line.split("=")[0].strip().split(" ")[0].strip()
    if datatype in PRIMITIVE_TYPES:
        name = line.split("=")[0].strip().split(" ")[1].strip()
        value = line.split("=")[1].strip()
        value, dt = do_value(value)
        if dt != datatype and dt is not None:
            raise SyntaxError(
                f"Datatype of {name} at line {variables_arduino.currentLineIndex} ({dt}) is not {datatype}")
        if variable_in_scope(name, variables_arduino.currentLineIndex):
            raise SyntaxError(f"Variable {name} at line {variables_arduino.currentLineIndex} already defined")
        add_variable_to_scope(name, datatype, variables_arduino.currentLineIndex)
        return f"{datatype} {name} = {value};"
    elif datatype in PRIMITIVE_ARRAY_TYPES:
        name = line.split("=")[0].strip().split(" ")[1].strip()
        value = line.split("=")[1].strip()
        value, dt = do_array_intializer(value)
        if dt != datatype[6:-1]:
            raise SyntaxError(
                f"Datatype of {name} at line {variables_arduino.currentLineIndex} ({dt}) is not {datatype}")
        if variable_in_scope(name, variables_arduino.currentLineIndex):
            raise SyntaxError(f"Variable {name} at line {variables_arduino.currentLineIndex} already defined")
        add_variable_to_scope(name, datatype, variables_arduino.currentLineIndex)
        return f"{datatype[6:-1]} {name}[] = {value};"
    else:
        raise SyntaxError(f"Datatype {datatype} at line {variables_arduino.currentLineIndex} is not defined")


def do_variable_assignment(line):
    """
    :param line: The complete line of the variable assignment
    :return: The assignment converted to C++
    """
    line = line.strip()
    name = line.split("=")[0].strip()
    value = line.split("=")[1].strip()
    value, dt = do_value(value)
    if not variable_in_scope(name, variables_arduino.currentLineIndex):
        raise SyntaxError(f"Variable {name} at line {variables_arduino.currentLineIndex} not defined")
    if dt != variable_in_scope(name, variables_arduino.currentLineIndex)[1] and dt is not None:
        raise SyntaxError(f"Datatype of {name} at line {variables_arduino.currentLineIndex} is not {dt}")
    return f"{name} = {value};"


def do_if(line):
    col_index = line.index("if") + 2
    if line.strip()[-1] == ":":
        row = variables_arduino.currentLineIndex
        col = len(line) - 1
        condition = do_value(line[col_index + 1:col])[0]
        if variables_arduino.identations[row] + 1 != variables_arduino.identations[row + 1]:
            raise SyntaxError(f"Expected indentation at line {row + 1}, (indentation = 4 Spaces)")
        for i in range(row + 1, variables_arduino.totalLineCount):
            if variables_arduino.identations[i] < variables_arduino.identations[row + 1]:
                end_indentation_index = i - 1
                break
        else:
            end_indentation_index = variables_arduino.totalLineCount - 1
        variables_arduino.code_done.append(f"if ({condition}) {{")
        if_code = []
        while variables_arduino.currentLineIndex < end_indentation_index:
            variables_arduino.currentLineIndex, l = next(variables_arduino.iterator)
            if_code.append(do_line(l))
        if_code.append("}")
        return "\n".join(if_code)
    else:
        raise SyntaxError(f"Expected ':' at line {variables_arduino.currentLineIndex} col {col_index}")


def do_while(line):
    col_index = line.index("while") + 5
    if line.strip()[-1] == ":":
        row = variables_arduino.currentLineIndex
        col = len(line) - 1
        condition = do_value(line[col_index + 1:col])[0]
        if variables_arduino.identations[row] + 1 != variables_arduino.identations[row + 1]:
            raise SyntaxError(f"Expected indentation at line {row + 1}, (indentation = 4 Spaces)")
        for i in range(row + 1, variables_arduino.totalLineCount):
            if variables_arduino.identations[i] < variables_arduino.identations[row + 1]:
                end_indentation_index = i - 1
                break
        else:
            end_indentation_index = variables_arduino.totalLineCount - 1
        variables_arduino.code_done.append(f"while ({condition}) {{")
        while_code = []

        while variables_arduino.currentLineIndex < end_indentation_index:
            variables_arduino.currentLineIndex, l = next(variables_arduino.iterator)
            while_code.append(do_line(l))
        while_code.append("}")
        return "\n".join(while_code)
    else:
        raise SyntaxError(f"Expected ':' at line {variables_arduino.currentLineIndex} col {col_index}")


def do_for(line):
    col_index = line.index("for") + 3
    if line.strip()[-1] == ":":
        row = variables_arduino.currentLineIndex
        elements = [x.strip() for x in line[col_index + 1:-1].split("in")]
        dt = "int[]"
        if len(elements) != 2:
            raise SyntaxError(f"Expected 'in' at line {variables_arduino.currentLineIndex} col {col_index}")
        counter_variable = elements[0]
        if variables_arduino.identations[row] + 1 != variables_arduino.identations[row + 1]:
            raise SyntaxError(f"Expected indentation at line {row + 1}, (indentation = 4 Spaces)")
        for i in range(row + 1, variables_arduino.totalLineCount):
            if variables_arduino.identations[i] < variables_arduino.identations[row + 1]:
                end_indentation_index = i - 1
                break
        else:
            end_indentation_index = variables_arduino.totalLineCount - 1

        if elements[1][:5] == "range":
            if elements[1][5] != "(":
                raise SyntaxError(f"Expected '(' at line {variables_arduino.currentLineIndex} col {col_index}")
            end_row, end_col = find_closing_bracket("(", row, variables_arduino.code[row].index("range") + 6)
            if end_row != row:
                raise SyntaxError(f"Expected ')' at line {end_row + 1} col {end_col + 1}")
            range_arguments, range_kwargs = do_arguments(elements[1][6:-1])
            if any([x[1] != "int" and x[1] != "short" and x[1] != "long" and x[1] is not None for x in
                    range_arguments]):
                raise SyntaxError(
                    f"Expected type numeric type (int, short, long) as range argument in line {variables_arduino.currentLineIndex}")
            if len(range_kwargs) != 0:
                raise SyntaxError(
                    f"Unexpected keyword arguments in range function in line {variables_arduino.currentLineIndex}")

            if len(range_arguments) == 1:
                for_code = [
                    f"for (int {counter_variable} = 0; {counter_variable} < {range_arguments[0][0]} ; {counter_variable}++) {{"]
            elif len(range_arguments) == 2:
                for_code = [
                    f"for (int {counter_variable} = {range_arguments[0][0]}; {counter_variable} < {range_arguments[1][0]} ; {counter_variable}++) {{"]
            elif len(range_arguments) == 3:
                for_code = [
                    f"for (int {counter_variable} = {range_arguments[0][0]}; {counter_variable} < {range_arguments[1][0]} ; {counter_variable} += {range_arguments[2][0]}) {{"]
            else:
                raise SyntaxError(
                    f"Expected 1, 2 or 3 arguments in range() at line {variables_arduino.currentLineIndex} col {col_index}")

        else:
            val, dt = do_value(elements[1])
            if dt[:5] == "array":

                for_code = [

                    f"for (int {(sys_var := next_sys_variable())} = 0; {sys_var} < sizeof({do_value(elements[1])[0]}) / sizeof(*{do_value(elements[1])[0]}); {sys_var}++) {{",
                    f"auto {counter_variable} = {do_value(elements[1])[0]}[{sys_var}];"]
            else:
                raise SyntaxError("Expected array or range() in for loop")
        add_variable_to_scope(counter_variable, dt[:-2], variables_arduino.currentLineIndex)
        [variables_arduino.code_done.append(x) for x in for_code]
        for_code = []
        while variables_arduino.currentLineIndex < end_indentation_index:
            variables_arduino.currentLineIndex, l = next(variables_arduino.iterator)
            for_code.append(do_line(l))
        for_code.append("}")
        return "\n".join(for_code)
    else:
        raise SyntaxError(f"Expected ':' at line {variables_arduino.currentLineIndex} col {col_index}")


def do_value(value) -> (str, str):
    print(value)
    if len(value) == 0:
        return "", None
    if value[0] == '"' == value[-1]:
        return value, "string"
    value = value.strip()
    valueList = []
    last_function_end = 0
    for i in range(len(value) - 1):
        if value[i + 1] == "(" and value[i] in VALID_NAME_LETTERS:
            for j in range(i, -1, -1):
                if j == " ":
                    start_col = j + 1
                    break
            else:
                start_col = 0
            end_col = find_closing_bracket_in_value(value, "(", i + 1)
            valueList.append(do_value(value[last_function_end:start_col]))
            valueList.append(check_function_execution(value[start_col:end_col + 1]))
            last_function_end = end_col + 1

    if len(valueList) > 0:
        valueList.append(do_value(value[last_function_end:]))
        # TODO return datatype here
        return " ".join([x[0] for x in valueList]), valueList[0][1]

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
            if value[i] not in NUMBERS and value[i] != "." and value[i] != " ":
                break
        else:
            if "." in value:
                return value, "float"
            else:
                return value, "int"
        raise SyntaxError(f"Value {value} at line {variables_arduino.currentLineIndex} is not a number")

    elif value[0] == '"':
        if value[-1] == '"':
            return value, "string"
        raise SyntaxError(f"Value {value} at line {variables_arduino.currentLineIndex} is not a string")
    elif value[0] == "'":
        if value[2] == "'" and len(value) == 3:
            return value, "char"
        raise SyntaxError(f"Value {value} at line {variables_arduino.currentLineIndex} is not a character")

    elif value[0] == "[":
        raise NotImplementedError("Lists are not implemented yet")


    elif value[0] == "(":
        raise NotImplementedError("Tuples are not implemented yet")

    elif value[0] == "T" and value[1] == "r" and value[2] == "u" and value[3] == "e" and len(value) == 4:
        return "true", "bool"

    elif value[0] == "F" and value[1] == "a" and value[2] == "l" and value[3] == "s" and value[4] == "e" and len(
            value) == 5:
        return "false", "bool"

    elif value[0] == "n" and value[1] == "o" and value[2] == "n" and value[3] == "e" and len(value) == 4:
        return "nullptr", "none"

    elif (s := variable_in_scope(value, variables_arduino.currentLineIndex)) is not None:
        return value, s[1]

    elif (f := check_function_execution(value)) is not None:
        return f[0], f[1]
    else:
        raise SyntaxError(f"Value '{value}' at line {variables_arduino.currentLineIndex} is not defined")


def do_array_intializer(value):
    args, kwargs = do_arguments(value[1:-1])
    if len(kwargs) != 0:
        raise SyntaxError(
            f"wtf? what is an = sign doing in an array intialization? at line {variables_arduino.currentLineIndex}")
    dt = args[0][1]
    if any([x[1] != dt for x in args]):
        raise SyntaxError(f"Array at line {variables_arduino.currentLineIndex} has different datatypes")
    return f"{{{', '.join([x[0] for x in args])}}}", dt


def add_variable_to_scope(name, datatype, line_index):
    for start, end in variables_arduino.scope.keys():
        if start <= line_index <= end:
            variables_arduino.scope[(start, end)][0].append((name, datatype))
            return


def variable_in_scope(name, line_index):
    """
    :return: (name, datatype) if variable is in scope, else None
    """
    for start, end in variables_arduino.scope.keys():
        if start <= line_index <= end:
            for i in variables_arduino.scope[(start, end)][0]:
                if i[0] == name:
                    return i


def get_line_identation(line):
    """
    :return: Indentation level of the line ALWAYS ROUNDS DOWN
    """
    return (len(line) - len(line.lstrip())) // DEFAULT_INDEX_LEVEL
