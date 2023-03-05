from server.transpiler.variable import *


class Function:
    @staticmethod
    def standard_call(args: list[Variable], name: str, transpiler: 'Transpiler'):
        return f"{name}({', '.join([i.name for i in args])})"

    def __init__(self, name: str, return_type: PyduinoType, args: list[Variable], on_call=standard_call,
                 pythonic_overload=False, position: Position = None, decorator: Decorator = None):
        self.name = name
        self.position = position
        self.return_type = return_type
        self.args = args
        self.kwargs = None
        self.on_call = on_call
        self.code = []
        self.called = False
        self.pythonic_overload = pythonic_overload  # if true, the function can be called with a variable number of arguments
        self.decorator = decorator
        self.remote_id = None

    def resolve_decorator(self, transpiler: 'Transpiler'):

        self.remote_id = transpiler.data.remote_function_count
        transpiler.data.remote_function_count += 1

        if not self.return_type.is_type(PyduinoVoid()):
            possible, s = self.return_type.type_to_bytes()
            if not possible:
                transpiler.data.newError(s, self.position)
                return

        for arg in self.args:
            possible, s = arg.type.type_to_bytes()
            if not possible:
                transpiler.data.newError(s, arg.location)
                return

        if self.decorator == Decorator.MAIN and transpiler.mode == "main":

            code = [f"void remote_{self.name}(char* data, char* outgoing) {{"]
            if self.args:
                maxsize = max([i.type.SIZE_BYTES for i in self.args])

                code.append(f"char temp_buffer[{maxsize}];")
                current_size = 0
                for arg in self.args:
                    for i in range(arg.type.SIZE_BYTES):
                        code.append(f"temp_buffer[{i}] = data[{current_size}];")
                        current_size += 1

                    code.append(
                        f"{arg.type.c_typename()} {arg.name} = {arg.type.bytes_to_type('temp_buffer')[1].name};")

            if not self.return_type.is_type(PyduinoVoid()):
                code.append(
                    f"{self.return_type.c_typename()} result = {self.on_call(self.args, self.name, transpiler)};")
                self.return_type.name = "result"

                code.append(f"char *temp_buffer_2;")
                code.append(f"temp_buffer_2 = {self.return_type.type_to_bytes()[1]};")

                for i in range(self.return_type.SIZE_BYTES):
                    code.append(f"outgoing[{i}] = temp_buffer_2[{i}];")
            else:
                code.append(f"{self.on_call(self.args, self.name, transpiler)};")
            code.append("}")
            self.code.extend(code)
            self.called = True
            transpiler.connection_needed = True
            transpiler.data.remote_functions.append(self)

        elif self.decorator == Decorator.BOARD and transpiler.mode == "board":
            raise NotImplementedError("Board functions are not implemented yet")

        elif (self.decorator == Decorator.MAIN and transpiler.mode == "board") or (
                self.decorator == Decorator.BOARD and transpiler.mode == "main"):
            if transpiler.mode == "main":
                code = [
                    f"{self.return_type.c_typename()} {self.name}(Arduino arduino, {', '.join([f'{arg.type.c_typename()} {arg.name}' for arg in self.args])}) {{"]
            else:
                code = [
                    f"{self.return_type.c_typename()} {self.name}({', '.join([f'{arg.type.c_typename()} {arg.name}' for arg in self.args])}) {{"]

            if self.args:
                sum_size = sum([i.type.SIZE_BYTES for i in self.args])

                code.append(f"char outgoing_buffer[{sum_size + 1}];")
                code.append(f"outgoing_buffer[0] = {self.remote_id};")
                code.append(f"char *temp_buffer;")
                current_size = 0
                for arg in self.args:
                    code.append(f"temp_buffer = {arg.type.type_to_bytes()[1]};")
                    for i in range(arg.type.SIZE_BYTES):
                        code.append(f"outgoing_buffer[{current_size + i + 1}] = temp_buffer[{i}];")
                    current_size += arg.type.SIZE_BYTES
            else:
                sum_size = 0
                code.append(f"char outgoing_buffer[{sum_size + 1}];")
                code.append(f"outgoing_buffer[0] = {self.remote_id};")

            if transpiler.mode == "main":
                code.append(f"char request_id = arduino.next_request_id();")
                code.append(f"arduino.send_request('m', outgoing_buffer, {sum_size + 1},request_id);")

                if not self.return_type.is_type(PyduinoVoid()):
                    code.append(f"{self.return_type.c_typename()} result;")
                    code.append(
                        f"delete new Promise<{self.return_type.c_typename()}>(&result, Arduino::{self.return_type.ARDUINO_BYTE_CONVERSION}, request_id, arduino.Responses);")
                    code.append(f"return result;}}")
                else:
                    code.append(f"delete new Promise<void>(nullptr, nullptr, request_id, arduino.Responses);}}")

            else:
                code.append(f"char request_id = getNextRequestId();")
                code.append(f"sendRequest('m', outgoing_buffer, {sum_size + 1}, request_id);")
                code.append(f"while ((Responses[request_id][0]) == 0) {{\ncheckSerial();\n}}")
                code.append(f"Responses[request_id][0] = 0;")

                if not self.return_type.is_type(PyduinoVoid()):
                    code.append(f"char temp_buffer2[{self.return_type.SIZE_BYTES}];")
                    for i in range(self.return_type.SIZE_BYTES):
                        code.append(f"temp_buffer2[{i}] = Responses[request_id][{i + 1}];")
                    code.append(f"return {self.return_type.bytes_to_type('temp_buffer2')[1].name};}}")
                else:
                    code.append(f"}}")
            transpiler.connection_needed = True
            self.code = code

    @staticmethod
    def check_definition(instruction: list[Token], transpiler: 'Transpiler'):

        if instruction[0].type not in [Datatype.INT, Datatype.FLOAT, Datatype.BOOL, Datatype.VOID, Datatype.STRING]:
            return False

        if len(instruction) < 3:
            return False

        instruction_types = [i.type for i in instruction]
        if Separator.ASSIGN in instruction_types:
            return False

        decorator = None
        if transpiler.data.current_decorator:
            decorator = transpiler.data.current_decorator
            transpiler.data.current_decorator = None

            if decorator == Decorator.UNKNOWN:
                transpiler.data.newError(f"Unknown decorator: '{decorator}'",
                                         Range(instruction[0].location.start.line - 1, 0, complete_line=True,
                                               data=transpiler.data))

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
        last_comma = -1
        arguments = []
        for i, arg in enumerate(args.inside):
            if arg.type == Separator.COMMA or i == len(args.inside) - 1:
                if i == len(args.inside) - 1:
                    i += 1
                if i != last_comma + 3:
                    transpiler.data.newError(
                        f"Invalid function argument definition: '{''.join([str(a) for a in args.inside[i:]])}'",
                        arg.location)
                    break
                datatype = args.inside[last_comma + 1]
                datatype = PyduinoType.get_type_from_token([datatype])
                if not datatype:
                    transpiler.data.newError(f"Invalid datatype in function argument definition: '{datatype}'",
                                             datatype.location)

                arg_name = args.inside[last_comma + 2]
                if arg_name.type != Word.IDENTIFIER:
                    transpiler.data.newError(f"Invalid name in function argument definition: '{arg_name.value}'",
                                             arg_name.location)
                last_comma = i
                var = Variable(arg_name.value, datatype, arg_name.location)
                transpiler.scope.add_Variable(var, transpiler.location.position.add_line(1))
                arguments.append(var)

        func = Function(name.value, return_type, arguments, decorator=decorator)
        transpiler.scope.add_Function(func, transpiler.location.position)

        code_done_start_index = len(transpiler.data.code_done)

        transpiler.data.code_done.append(
            f"{return_type.c_typename()} {name.value}({', '.join([f'{arg.type.c_typename()} {arg.name}' for arg in arguments])}) {{")

        end_line = StringUtils.get_indentation_range(transpiler.location.position.line + 1, transpiler)
        prev = transpiler.data.in_function
        transpiler.data.in_function = func
        transpiler.transpileTo(end_line)
        transpiler.data.in_function = prev
        transpiler.data.code_done.append("}")
        func.code = transpiler.data.code_done[code_done_start_index:]
        func.resolve_decorator(transpiler)
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
            transpiler.data.newError(
                f"Cannot return '{type}' in function returning '{transpiler.data.in_function.return_type}'",
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

        func = transpiler.scope.get_Function(instruction[0].value, instruction[0].location.start)
        if not func:
            transpiler.data.newError(f"Function '{instruction[0].value}' is not defined", instruction[0].location)
            return True

        args = instruction[1].inside
        args_c = []
        arg_count = 0
        last_comma = 0
        for i in range(0, len(args)):
            if args[i].type == Separator.COMMA or i == len(args) - 1:

                if i == len(args) - 1:
                    i += 1
                arg = args[last_comma:i]
                arg = Value.do_value(arg, transpiler)
                last_comma = i + 1
                if not func.pythonic_overload:
                    if arg_count >= len(func.args) and not func.pythonic_overload:
                        transpiler.data.newError(f"Too many arguments passed to function '{func.name}'",
                                                 Range.fromPositions(args[0].location.start, args[-1].location.end))
                        return True

                    expected_datatype = func.args[arg_count].type

                    if not expected_datatype.is_type(arg.type):
                        transpiler.data.newError(
                            f"Cannot pass '{arg.type}' to function '{func.name}' expecting '{expected_datatype}'",
                            arg.location)

                arg_count += 1
                args_c.append(arg)

        if arg_count < len(func.args) and not func.pythonic_overload:
            if arg_count == 0:
                transpiler.data.newError(f"Not enough arguments passed to function '{func.name}'",
                                         instruction[1].location)
            else:
                transpiler.data.newError(f"Not enough arguments passed to function '{func.name}'",
                                         Range.fromPositions(args[0].location.start, args[-1].location.end))
            return True

        func.called = True
        if func.return_type.is_type(PyduinoVoid()):
            transpiler.data.code_done.append(func.on_call(args_c, func.name, transpiler) + ";")
            return True
        else:
            var = transpiler.utils.next_sysvar()
            transpiler.data.code_done.append(
                f"{func.return_type.c_typename()} {var} = {func.on_call(args_c, func.name, transpiler)};")
            return Variable(var, func.return_type, instruction[0].location)


    @staticmethod
    def check_decorator(instruction: list[Token], transpiler: 'Transpiler') -> bool:
        # TODO hast to be checked after functions
        if transpiler.data.current_decorator is not None:
            transpiler.data.newError("Missplaced decorator",
                                     Range(instruction[0].location.start.line - 1, 0, complete_line=True,
                                           data=transpiler.data))

        if instruction[0].type not in Decorator.DECORATORS:
            return False

        if len(instruction) != 1:
            transpiler.data.newError("Decorator has to be alone on line",
                                     Range.fromPositions(instruction[1].location.start, instruction[-1].location.end))

        if instruction[0].type == Decorator.UNKNOWN:
            transpiler.data.newError("Unknown decorator", instruction[0].location)

        transpiler.data.current_decorator = instruction[0].type
        return True


class Builtin(Function):
    def __init__(self, name: str, return_type: PyduinoType, args: list[Variable], on_call,
                 pythonic_overload: bool = False):
        super().__init__(name, return_type, args, pythonic_overload=pythonic_overload, position=Position(0, 0))
        self.on_call = on_call

    @staticmethod
    def add_builtins(transpiler: 'Transpiler'):
        transpiler.scope.functions.extend([
            Builtin("print", PyduinoVoid(), [], Builtin.print, pythonic_overload=True),
            Builtin("len", PyduinoInt(), [Variable("args", PyduinoArray(PyduinoAny()), Range(0, 0))], Builtin.len),
            Builtin("millis", PyduinoInt(), [], Builtin.millis),
            Builtin("delay", PyduinoVoid(), [Variable("args", PyduinoInt(), Range(0, 0))], Builtin.delay),
            Builtin("analogRead", PyduinoInt(), [Variable("args", PyduinoInt(), Range(0, 0))], Builtin.analogRead),
            Builtin("analogWrite", PyduinoVoid(), [Variable("args", PyduinoInt(), Range(0, 0)),
                                                   Variable("args", PyduinoInt(), Range(0, 0))], Builtin.analogWrite),
            Builtin("digitalRead", PyduinoInt(), [Variable("args", PyduinoInt(), Range(0, 0))], Builtin.digitalRead),
            Builtin("digitalWrite", PyduinoVoid(), [Variable("args", PyduinoInt(), Range(0, 0)),
                                                    Variable("args", PyduinoInt(), Range(0, 0))], Builtin.digitalWrite),

        ])

    @staticmethod
    def print(args: list[Variable], name: str, transpiler: 'Transpiler'):
        var = transpiler.utils.next_sysvar()
        if transpiler.mode == "main":
            transpiler.data.code_done.append(f"string {var} = \"\";")
        else:
            transpiler.data.code_done.append(f"String {var} = \"\";")

        for arg in args:

            possible, s = arg.type.to_string()
            if not possible:
                transpiler.data.newError(f"Cannot print {arg.type}, {s}", arg.location)
                return False
            transpiler.data.code_done.append(f'{var} += {s.name}; {var} += " ";')

        if transpiler.mode == "main":
            transpiler.data.code_done.append(f"cout << {var} << endl;")
        else:
            transpiler.data.code_done.append(f"print({var},{len(args)});")
            transpiler.connection_needed = True

        return ""

    @staticmethod
    def len(args: list[Variable], name: str, transpiler: 'Transpiler'):
        return f"(int)(sizeof({args[0].name}) / sizeof({args[0].name})[0])"

    @staticmethod
    def millis(args: list[Variable], name: str, transpiler: 'Transpiler'):
        if transpiler.mode == "board":
            return f"millis()"
        else:
            return f"(int)std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - start_time).count()"

    @staticmethod
    def delay(args: list[Variable], name: str, transpiler: 'Transpiler'):
        if transpiler.mode == "board":
            return f"better_delay({args[0].name})"
        else:
            return f"std::this_thread::sleep_for(std::chrono::milliseconds({args[0].name}))"

    @staticmethod
    def analogRead(args: list[Variable], name: str, transpiler: 'Transpiler'):
        if transpiler.mode == "board":
            return f"analogRead(analogPorts[{args[0].name}])"
        else:
            transpiler.connection_needed = True
            return f"arduino.analogRead({args[0].name})"

    @staticmethod
    def analogWrite(args: list[Variable], name: str, transpiler: 'Transpiler'):
        if transpiler.mode == "board":
            return f"analogWrite({args[0].name}, {args[1].name})"
        else:
            transpiler.connection_needed = True
            return f"arduino.analogWrite({args[0].name}, {args[1].name})"

    @staticmethod
    def digitalRead(args: list[Variable], name: str, transpiler: 'Transpiler'):
        if transpiler.mode == "board":
            return f"digitalRead({args[0].name})"
        else:
            transpiler.connection_needed = True
            return f"arduino.digitalRead({args[0].name})"

    @staticmethod
    def digitalWrite(args: list[Variable], name: str, transpiler: 'Transpiler'):
        if transpiler.mode == "board":
            return f"digitalWrite({args[0].name}, {args[1].name})"
        else:
            transpiler.connection_needed = True
            return f"arduino.digitalWrite({args[0].name}, {args[1].name})"


if __name__ == '__main__':

    filenames = ["control.py", "function.py", "pyduino_utils.py", "runner.py", "transpiler.py", "scope.py",
                 "tokenizer.py", "variable.py", "../server.py", "SerialCommunication/Serial_PC.cpp",
                 "SerialCommunication/Serial_Arduino/Serial_Arduino.ino"]
    # count lines of code
    total = 0
    for filename in filenames:
        with open(filename, "r") as f:
            total += len(f.readlines())
    print(f"Total lines of code: {total}")

    # count words
    total = 0
    for filename in filenames:
        with open(filename, "r") as f:
            total += len(f.read().split())
    print(f"Total words of code: {total}")

    # count characters
    total = 0
    for filename in filenames:
        with open(filename, "r") as f:
            total += len(f.read())
    print(f"Total characters of code: {total}")
