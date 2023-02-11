from server.transpiler.variable import *


class Function:
    @staticmethod
    def standard_call(args: list[Variable], kwargs: list[Variable], transpiler: 'Transpiler', name: str):
        return f"{name}({', '.join([i.name for i in args])}, {', '.join([f'{i.name}' for i in kwargs])})"

    def __init__(self, name: str, return_type: PyduinoType, args: list[Variable], kwargs: list[Variable, Word], on_call=standard_call):
        self.name = name
        self.return_type = return_type
        self.args = args
        self.kwargs = kwargs
        self.on_call = on_call


    @staticmethod
    def check_definition(instruction: str, transpiler: 'Transpiler'):
        definition = instruction.split(' ', 1)

        if len(definition) < 2:
            return False

        return_type, name = definition[0], definition[1]

        return_type = PyduinoType.get_type_from_string(return_type)

        if not return_type:
            return False

        name = StringUtils.check_colon(name, transpiler)

        name, args = name.split('(', 1)
        name = name.strip()

        if not StringUtils.is_identifier(name):
            transpiler.data.newError(f"Invalid function name: '{name}'", transpiler.location.getRangeFromString(name))

        args_str, kwargs_str = transpiler.utils.get_arguments("(" + args)
        args, kwargs = [], []

        for arg in args_str:
            type_str, name_str = arg.split(' ', 1)
            type = PyduinoType.get_type_from_string(type_str)
            if not type:
                transpiler.data.newError(f"Invalid type for argument {name_str}: '{type_str}'", transpiler.location.getRangeFromString(type_str))
                type = PyduinoUndefined()

            if not StringUtils.is_identifier(name_str):
                transpiler.data.newError(f"Invalid function argument: '{name_str}'", transpiler.location.getRangeFromString(name_str))

            var = Variable(name_str, type)
            args.append(var)
            transpiler.scope.add_Variable(var, transpiler.location.position.add_line(1))

        for name_str, value_str in kwargs_str:
            type_str, name_str = name_str.split(' ', 1)
            type = PyduinoType.get_type_from_string(type_str)
            if not type:
                transpiler.data.newError(f"Invalid type for argument {name_str}: '{type_str}'", transpiler.location.getRangeFromString(type_str))
                type = PyduinoUndefined()

            if not StringUtils.is_identifier(name_str):
                transpiler.data.newError(f"Invalid function argument: '{name_str}'", transpiler.location.getRangeFromString(name_str))

            value = Word.do_value(value_str, transpiler)
            if not value:
                transpiler.data.newError(f"Invalid default value for argument {name_str}: '{value_str}'",
                                         transpiler.location.getRangeFromString(value_str))
                value = Word("None", PyduinoUndefined())

            if not type.is_type(value.type):
                transpiler.data.newError(f"Invalid default value for argument {name_str}: '{value_str}' is not of type {type}",
                                         transpiler.location.getRangeFromString(value_str))
            var = Variable(name_str, type)
            kwargs.append((var, value))
            transpiler.scope.add_Variable(var, transpiler.location.position.add_line(1))

        func = Function(name, return_type, args, kwargs)
        transpiler.scope.add_Function(func, transpiler.location.position)

        transpiler.data.code_done.append(
            f"{return_type} {name}({', '.join([f'{arg.type} {arg.name}' for arg in args] + [f'{kwarg[0].type} {kwarg[0].name} = {kwarg[1].name}' for kwarg in kwargs])}) {{")

        end_line = StringUtils.get_indentation_range(transpiler.location.position.line + 1, transpiler)
        prev = transpiler.data.in_function
        transpiler.data.in_function = func
        transpiler.transpileTo(end_line)
        transpiler.data.in_function = prev

        transpiler.data.code_done.append("}")

        return True

    @staticmethod
    def checK_return(instruction: str, transpiler: 'Transpiler'):
        if not instruction.startswith("return"):
            return False

        if not transpiler.data.in_function:
            transpiler.data.newError("Cannot 'return' outside of function", transpiler.location.getRangeFromString(instruction))
            return True

        type = instruction[6:].strip()

        if type == "":
            type = PyduinoVoid()
        else:
            var = Word.do_value(type, transpiler)
            type = var.type

        if not transpiler.data.in_function.return_type.is_type(type):
            transpiler.data.newError(f"Cannot return '{type}' in function returning '{transpiler.data.in_function.return_type}'",
                                     transpiler.location.getRangeFromString(instruction[6:].strip()))
            return True

        if type.is_type(PyduinoVoid()):
            transpiler.data.code_done.append("return;")
        else:
            transpiler.data.code_done.append(f"return {var.name};")
        return True

    @staticmethod
    def checK_call(instruction: str, transpiler: 'Transpiler'):
        name, args = instruction.split('(', 1)
        name = name.strip()
        if not StringUtils.is_identifier(name):
            return False











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
