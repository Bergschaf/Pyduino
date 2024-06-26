from server.transpiler.control import Control
from server.transpiler.function import Function, Builtin
from server.transpiler.scope import Scope
from server.transpiler.tokenizer import *
from server.transpiler.variable import *


class Transpiler:
    def __init__(self, code: list[str], mode="main", definition: bool = False, line_offset=0):
        """
        :param code: The Code to transpile (including the #main or #board)
        :param mode: main or board
        :param line_offset: The line offset of the code segment
        :param definition: If the code is in the definition part at the top of the file
        """
        self.mode = mode
        self.definition = definition
        self.connection_needed = False
        self.data: Data = Data(code, 0)
        self.location: CurrentLocation = CurrentLocation(code, self.data.indentations)

        self.utils: StringUtils = StringUtils(self.location, self.data, self)

        self.parent_indent = Token.tokenize_range(code, Position(line_offset, 0))
        self.current_indent = self.parent_indent

        self.scope: Scope = Scope(self)

        Builtin.add_builtins(self)

        self.checks = [Variable.check_assignment, Variable.check_definition, Control.check_condition,Control.check_break_continue,
                       Function.check_definition,
                       Function.check_return, Function.check_call,
                       Function.check_decorator]  # the functions to check for different instruction types

    def copy(self):
        return Transpiler(self.data.code, self.mode, self.definition, self.data.line_offset)

    def transpile(self):
        self.transpileRange(self.parent_indent)

    def transpileRange(self, indent: Indent):
        """
        Transpiles up to the given line
        """
        i = 0
        while True:
            try:
                id, line = next(indent.enumerator)
                self.current_indent = indent
                self.current_indent.index = id
            except StopIteration:
                #print("Stop Iteration")
                return

            else:
                try:
                    self.do_line(line)
                except InvalidLineError:
                    #print("Invalid Line")
                    # The line is invalid, so it is skipped
                    pass
                except Exception as e:  # TODO remove comment
                    #print("Something went wrong, line: ", self.location.position.line)
                    # Something went wrong
                    #print(e)
                    continue


    def do_line(self, line: list[Token]):

        if Separator.HASHTAG in [t.type for t in line]:
            line = line[:[t.type for t in line].index(Separator.HASHTAG)]

        if not line:
            return

        if line[-1].type == Separator.SEMICOLON:
            line = line[:-1]
            self.data.newError("We don't do that here", line[-1].location)

        if line[0].type == Indent.INDENT:
            self.data.newError("Unexpected indent", line[0].location)
            self.transpileRange(line[0])
            return

        if self.definition and self.data.in_function is None:
            if not Function.check_definition(line, self):
                if not Function.check_decorator(line, self):
                    self.data.newError("Code is not allowed in definition part",
                                       Range.fromPositions(line[0].location.start, line[-1].location.end))
            return

        for check in self.checks:
            if check(line, self):
                return
        self.data.newError("Unknow instruction", Range.fromPositions(line[0].location.start, line[-1].location.end))

    def finish(self) -> str:
        """
        TODO add String function here in the c++ version:
        std::string String(int value) { return std::to_string(value); }
        std::string String(float value) { return std::to_string(value); }
        for all datatypes

        :return:
        """
        # TODO DEFINE A VARIABLE '__tempstr__' TO STORE THE STRING CONVERSIONS
        code = []

        if self.mode == "main":
            if self.connection_needed:
                code.append('#include "../server/transpiler/SerialCommunication/Serial_PC.cpp"')
            code.append("#include <iostream>")
            code.append("#include <string>")
            code.append("#include <stdlib.h>")
            code.append("using namespace std;")
            code.append(f"#include <chrono>")
            code.append("#include <thread>")
            code.append("typedef int py_int;")
            code.append(
                "std::string String(int value) { return std::to_string(value); }\nstd::string String(float value) { return std::to_string(value); }\nstd::string String(std::string value) { return \"\\\"\" + value  + \"\\\"\"; }")
            code.append(
                "std::string String(char value) { return \"'\" + std::to_string(value) + \"'\"; }\nstd::string String(bool value) { return std::to_string(value); }")

            for f in self.scope.functions:
                if f.called:
                    code.extend(f.code)

            if self.connection_needed and self.data.remote_functions:
                code.append("void do_functions(Arduino arduino, char* data, char id, char request_id) {")
                temp_var = self.utils.next_sysvar()
                code.append(f"char {temp_var}[{max([i.return_type.SIZE_BYTES for i in self.data.remote_functions])}];")
                for f in self.data.remote_functions:
                    code.append(f"if (id == {f.remote_id}) {{")
                    code.append(f"remote_{f.name}(data,{temp_var});")
                    code.append(f"arduino.send_response({temp_var}, {f.return_type.SIZE_BYTES}, request_id);}}")
                code.append("}")

            code.append("int main() {")

            if self.connection_needed:

                code.append("Arduino arduino = Arduino();")
                if self.data.remote_functions:
                    code.append("arduino.do_function = do_functions;")

            code.append("auto start_time = std::chrono::steady_clock::now();")

            code.extend(self.data.code_done)

            if self.connection_needed:
                code.append("arduino.listenerThread->join();")
            code.append("return 0;")
            code.append("}")

        elif self.mode == "board":
            if self.connection_needed:
                with open("server/transpiler/SerialCommunication/Serial_Arduino/Serial_Arduino.ino") as f:
                    code.extend(f.readlines())
            else:
                with open("server/transpiler/SerialCommunication/Serial_Arduino/No_Connection_Arduino.ino") as f:
                    code.extend(f.readlines())

            if self.data.lcd_needed:
                code.append("#include <Wire.h>")
                code.append("#include <LiquidCrystal_I2C.h>")
                code.append("LiquidCrystal_I2C lcd(0x27, 16, 2);")
                code.append("""void createCustomChar(String input, int charIndex){
                  if(input.length() != 40){
                    // invalid Char
                    return;
                  }
                  byte customChar[8];
                
                    for(int i = 0; i < 8; i++){
                        String byteString = input.substring(i*5, i*5+5);
                        byteString.replace("0", " ");
                        byteString.replace("1", "0");
                        byteString.replace(" ", "1");
                        customChar[i] = strtol(byteString.c_str(), NULL, 2);
                    }
                    lcd.createChar(charIndex,customChar);
                }""")

            for f in self.scope.functions:
                if f.called:
                    code.extend(f.code)

            if self.connection_needed:
                code.append("void setup() {\n Serial.begin(256000); \nHandshake();\ndelay(10);")

                if self.data.lcd_needed:
                    code.append("lcd.init();lcd.backlight();")

                for i, line in enumerate(self.data.code_done):
                    code.append(line)
                    if i + 1 < len(self.data.code_done):
                        if not self.data.code_done[i+1].startswith("else"):
                            code.append("checkSerial();")
                code.append("} \n void loop() { checkSerial(); }")

            else:
                code.append("void setup() {")
                if self.data.lcd_needed:
                    code.append("lcd.init();lcd.backlight();")
                code.extend(self.data.code_done)
                code.append("} \nvoid loop() { }")

        return "\n".join(code)

    @staticmethod
    def get_transpiler(code: list[str]) -> tuple['Transpiler', 'Transpiler', 'Transpiler']:

        error = False
        line_offset_main = 0
        line_offset_board = 0
        main_code = []
        board_code = []
        definition_code = []

        for i in range(len(code)):
            if code[i] == "#main" or code[i] == "# main":
                definition_code = code[:i]
                line_offset_main = i + 1
                for i in range(len(code)):
                    if code[i] == "#board" or code[i] == "# board":
                        board_code = code[i + 1:]
                        line_offset_board = i + 1
                        main_code = code[line_offset_main:i]
                        break
                else:
                    main_code = code[line_offset_main:]
                break

            if code[i] == "#board" or code[i] == "# board":
                definition_code = code[:i]
                line_offset_board = i + 1
                for i in range(len(code)):
                    if code[i] == "#main" or code[i] == "# main":
                        board_code = code[line_offset_board:i]
                        main_code = code[i + 1:]
                        line_offset_main = i + 1
                        break
                else:
                    board_code = code[line_offset_board:]
                break
        else:
            definition_code = code
            error = True

        if main_code:
            main_transpiler = Transpiler(main_code, mode="main", line_offset=line_offset_main)
        else:
            main_transpiler = None

        if board_code:
            board_transpiler = Transpiler(board_code, mode="board", line_offset=line_offset_board)
        else:
            board_transpiler = None

        if definition_code:
            definition_transpiler = Transpiler(definition_code, definition=True, line_offset=0)
        else:
            definition_transpiler = None

        if definition_transpiler and error:
            definition_transpiler.data.newError("Missing #main or #board part in the code",
                                                Range(0, 0, complete_line=True, data=definition_transpiler.data))

        return main_transpiler, board_transpiler, definition_transpiler

    @staticmethod
    def get_code(code: list[str]) -> tuple[str, str]:
        main, board, definition_main = Transpiler.get_transpiler(code)
        code_main = ""
        code_board = ""
        if definition_main:
            definition_board = definition_main.copy()
            definition_board.mode = "board"

            definition_main.transpile()
            definition_board.transpile()
            if main:
                main.scope.add_functions(definition_main.scope.functions)
                main.data.remote_functions.extend(definition_main.data.remote_functions)
                main.data.errors.extend(definition_main.data.errors)
                if definition_main.connection_needed:
                    main.connection_needed = True
            if board:
                board.scope.add_functions(definition_board.scope.functions)
                board.data.remote_functions.extend(definition_board.data.remote_functions)
                board.data.errors.extend(definition_board.data.errors)
                if definition_board.connection_needed:
                    board.connection_needed = True

        if board:
            board.transpile()
        if main:
            main.transpile()

            if main.data.errors:
                print("Errors in main:")
                print(main.data.errors)
                raise Exception("Errors in main")

            if board:
                main.connection_needed = True if board.connection_needed else main.connection_needed
            else:
                if main.connection_needed:
                    with open("server/transpiler/SerialCommunication/Serial_Arduino/Serial_Arduino.ino") as f:
                        code_board = f.read()
                    code_board += "void setup() {\n Serial.begin(256000); \nHandshake();} \n void loop() { checkSerial(); }"

            code_main = main.finish()

        if board:
            board.transpile()

            if board.data.errors:
                print("Errors in board:")
                print(board.data.errors)
                raise Exception("Errors in board")

            if main:
                board.connection_needed = True if main.connection_needed else board.connection_needed
            else:
                if board.connection_needed:
                    code_main = '''#include "../server/transpiler/SerialCommunication/Serial_PC.cpp"\nint main(){\nArduino arduino = Arduino();
                    arduino.listenerThread->join();return 0;}'''

            code_board = board.finish()

        return code_main, code_board

    @staticmethod
    def get_diagnostics(code: list[str]) -> list[Error]:
        main, board, definition_main = Transpiler.get_transpiler(code)
        diagnostics = []
        if definition_main:
            definition_board = definition_main.copy()
            definition_board.mode = "board"

            definition_main.transpile()
            definition_board.transpile()
            diagnostics.extend([e.get_Diagnostic(definition_main) for e in definition_main.data.errors])
            if main:
                main.scope.add_functions(definition_main.scope.functions)

            if board:
                board.scope.add_functions(definition_board.scope.functions)

        if main:
            main.transpile()
            diagnostics.extend([e.get_Diagnostic(main) for e in main.data.errors])
        if board:
            board.transpile()
            diagnostics.extend([e.get_Diagnostic(board) for e in board.data.errors])
        return diagnostics


if __name__ == '__main__':
    Transpiler = Transpiler(
        code=["int[][] x = [[1, 2, 3], [4, 5, 6]]", "int y = x[0][0]", "int z = x[1][2]", "int a = x[1][0]"],
        mode='main', line_offset=0)
    print(Transpiler.transpileTo(10))
    print(Transpiler.data.code_done)
    print([str(e) for e in Transpiler.data.errors])
