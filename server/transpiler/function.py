from server.transpiler.variable import *


class Function:
    @staticmethod
    def standard_call(args: list[Variable], name: str, transpiler: 'Transpiler'):
        return f"{name}({', '.join([i.name for i in args])})"

    def __init__(self, name: str, return_type: PyduinoType, args: list[Variable], on_call=standard_call):
        self.name = name
        self.return_type = return_type
        self.args = args
        self.kwargs = None
        self.on_call = on_call

    @staticmethod
    def check_definition(instruction: list[Token], transpiler: 'Transpiler'):

        if instruction[0].type not in [Datatype.INT, Datatype.FLOAT, Datatype.BOOL, Datatype.VOID, Datatype.STRING]:
            return False

        instruction_types = [i.type for i in instruction]
        if Separator.ASSIGN in instruction_types:
            return False

        if instruction[1].type != Word.IDENTIFIER:
            transpiler.data.newError(f"Invalid function name: '{instruction[1].value}'", instruction[1].location)

        return_type, name, args = instruction[0], instruction[1], instruction[2:]

        return_type = PyduinoType.get_type_from_token([return_type])

        if not return_type:
            return False

        args = StringUtils.check_colon(args, transpiler)

        if args[0].type != Brackets.ROUND:
            transpiler.data.newError(f"Invalid function argument definition: '{args[0].value}'", args[0].location)
            return True

        args = args[0]
        last_comma = 0
        arguments = []
        for i, arg in enumerate(args.inside):
            if arg.type == Separator.COMMA:
                if i != last_comma + 3:
                    transpiler.data.newError(f"Invalid function argument definition: '{''.join()}'", arg.location)
                    return True
                datatype = args.inside[last_comma + 1]
                datatype = PyduinoType.get_type_from_token([datatype])
                if not datatype:
                    transpiler.data.newError(f"Invalid datatype in function argument definition: '{datatype}'", datatype.location)

                name = args.inside[last_comma + 2]
                if name.type != Word.IDENTIFIER:
                    transpiler.data.newError(f"Invalid name in function argument definition: '{name.value}'", name.location)
                last_comma = i
                var = Variable(datatype, name.value, name.location)
                transpiler.scope.add_Variable(var, transpiler.location.position.add_line(1))
                arguments.append(var)

        func = Function(name.value, return_type, arguments)
        transpiler.scope.add_Function(func, transpiler.location.position)

        transpiler.data.code_done.append(
            f"{return_type} {name.value}({', '.join([f'{arg.type} {arg.name}' for arg in arguments])}) {{")

        end_line = StringUtils.get_indentation_range(transpiler.location.position.line + 1, transpiler)
        prev = transpiler.data.in_function
        transpiler.data.in_function = func
        transpiler.transpileTo(end_line)
        transpiler.data.in_function = prev
        transpiler.data.code_done.append("}")

        return True

    @staticmethod
    def check_return(instruction: list[Token], transpiler: 'Transpiler'):
        if instruction[0].type != Keyword.RETURN:
            return False

        if not transpiler.data.in_function:
            transpiler.data.newError("Cannot 'return' outside of function", instruction[0].location)
            return True

        if len(instruction) == 1:
            type = PyduinoVoid()

        else:
            var = Value.do_value(instruction[1:], transpiler)
            type = var.type

        if not transpiler.data.in_function.return_type.is_type(type):
            transpiler.data.newError(f"Cannot return '{type}' in function returning '{transpiler.data.in_function.return_type}'",
                                     Range.fromPositions(instruction[0].location.start, instruction[-1].location.end))
            return True

        if type.is_type(PyduinoVoid()):
            transpiler.data.code_done.append("return;")
        else:
            transpiler.data.code_done.append(f"return {var.name};")
        return True

    @staticmethod
    def check_call(instruction: list[Token], transpiler: 'Transpiler') -> bool:
        if len(instruction) != 2:
            return False

        if instruction[1].type != Brackets.ROUND:
            return False

        if instruction[0].type != Word.IDENTIFIER:
            return False

        func = transpiler.scope.get_Function(instruction[0].value, transpiler.location.position)
        if not func:
            transpiler.data.newError(f"Function '{instruction[0].value}' is not defined", instruction[0].location)
            return True

        args = instruction[1].inside
        args_c = []
        arg_count = 0
        last_comma = 0
        for i in range(0, len(args)):
            if args[i].type == Separator.COMMA:
                arg = args[last_comma:i]
                last_comma = i + 1

                if arg_count >= len(func.args):
                    transpiler.data.newError(f"Too many arguments passed to function '{func.name}'",
                                             Range.fromPositions(arg[0].location.start, arg[-1].location.end))
                    return True

                expected_datatype = func.args[arg_count].type

                arg = Value.do_value(arg, transpiler)

                if not arg.type.is_type(expected_datatype):
                    transpiler.data.newError(f"Cannot pass '{arg.type}' to function '{func.name}' expecting '{expected_datatype}'", arg.location)

                arg_count += 1
                args_c.append(arg)

        if arg_count < len(func.args):
            transpiler.data.newError(f"Not enough arguments passed to function '{func.name}'",
                                     Range.fromPositions(args[-1].location.start, args[-1].location.end))
            return True

        if func.return_type.is_type(PyduinoVoid()):
            transpiler.data.code_done.append(func.on_call(args_c, func.name, transpiler) + ";")
            return True
        else:
            var = transpiler.utils.next_sysvar()
            transpiler.data.code_done.append(f"{func.return_type} {var} = {func.on_call(args_c, func.name, transpiler)};")
            return Variable(var, func.return_type, instruction[0].location)


class Builtin(Function):
    def __init__(self, name: str, return_type: PyduinoType, args: list[Variable], kwargs: list[Variable, Word], on_call):
        super().__init__(name, return_type, args, kwargs)
        self.on_call = on_call

    @staticmethod
    def print(args: list[Variable], kwargs: list[Variable], transpiler: 'Transpiler', name):
        var = transpiler.utils.next_sysvar()

        transpiler.data.code_done.append(f"String {var} = \"\";")

        for arg in args:
            possible, s = arg.type.to_string()
            if not possible:
                transpiler.data.newError(f"Cannot print {arg.type}, {s}", transpiler.location.getRangeFromString(arg.name))
                return False
            transpiler.data.code_done.append(f"{var} += {s.name};")

        if transpiler.mode == "main":
            transpiler.data.code_done.append(f"cout << {var} << endl;")
        else:
            transpiler.data.code_done.append(f"print({var});")
        return ""
