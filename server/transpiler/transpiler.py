from server.transpiler.scope import Scope
from server.transpiler.variable import *
from server.transpiler.control import Control
from server.transpiler.function import Function
from server.transpiler.tokenizer import *


class Transpiler:
    def __init__(self, code: list[str], mode="main", definition: bool = True, line_offset=0):
        """
        :param code: The Code to transpile (including the #main or #board)
        :param mode: main or board
        :param line_offset: The line offset of the code segment
        :param definition: If the code is in the definition part at the top of the file
        """
        self.mode = mode
        self.definition = definition

        self.data: Data = Data(code, line_offset)
        self.location: CurrentLocation = CurrentLocation(code, self.data.indentations)

        self.utils: StringUtils = StringUtils(self.location, self.data, self)

        self.data.indentations = self.utils.getIndentations(self.data.code)
        self.location.indentations = self.data.indentations

        self.data.code_tokens = [Token.tokenize(line, Position(i, 0)) for i, line in enumerate(self.data.code)]
        self.data.enumerator = enumerate(self.data.code_tokens)

        self.scope: Scope = Scope(self.data, self.location)

        self.checks = [Variable.check_assignment, Variable.check_definition, Control.check_condition, Function.check_definition,
                       Function.check_return, Function.check_call, Function.check_decorator]  # the functions to check for different instruction types

    def next_line(self):
        index, line = next(self.data.enumerator)
        self.location.next_line()
        self.do_line(line)

    def copy(self):
        return Transpiler(self.data.code, self.mode, self.definition, self.data.line_offset)

    def transpileTo(self, line: int):
        """
        Transpiles up to the given line
        """
        while self.location.position.line < line:
            try:
                self.next_line()
            except StopIteration:
                print("Stop Iteration")
                # The end of the code is reached
                break
            except EndOfFileError:
                print("EOF")
                # The end of the code is reached
                break
            except InvalidLineError:
                print("Invalid Line")
                # The line is invalid, so it is skipped
                pass
            # except Exception as e: TODO remove comment
            #    print("Something went wrong, line: ", self.location.position.line)
            #    # Something went wrong
            #    print(e)
            #    break

    def do_line(self, line: list[Token]):
        if Separator.HASHTAG in [t.type for t in line]:
            line = line[:[t.type for t in line].index(Separator.HASHTAG)]

        if not line:
            return

        if line[-1].type == Separator.SEMICOLON:
            line = line[:-1]
            self.data.newError("We don't do that here", line[-1].location)

        for check in self.checks:
            if check(line, self):
                return

    def finish(self):
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
            if self.data.connection_needed:
                code.append("#include <Arduino.h>")

            code.append("int main() {")

            if self.data.connection_needed:
                code.append("Arduino arduino = Arduino();")

        elif self.mode == "board":
            pass

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
                line_offset_main = i
                for i in range(len(code)):
                    if code[i] == "#board" or code[i] == "# board":
                        board_code = code[i:]
                        line_offset_board = i
                        main_code = code[line_offset_main:i]
                        break
                else:
                    main_code = code[line_offset_main:]
                break

            elif code[0] == "#board" or code[0] == "# board":
                definition_code = code[:1]
                line_offset_board = i
                for i in range(len(code)):
                    if code[i] == "#main" or code[i] == "# main":
                        board_code = code[line_offset_board:i]
                        main_code = code[i:]
                        line_offset_main = i
                        break
                else:
                    board_code = code[line_offset_board:]
                break
        else:
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

        if error:
            main_transpiler.data.newError("Missing #main or #board part in the code",
                                          Range(0, 0, complete_line=True, data=main_transpiler.data))

        return main_transpiler, board_transpiler, definition_transpiler

    @staticmethod
    def transpile(code: list[str]) -> tuple[list[str], list[Error]]:
        main, board, definition_main = Transpiler.get_transpiler(code)

        definition_board = definition_main.copy()
        definition_board.mode = "board"

        definition_main.transpileTo(len(definition_main.data.code))
        definition_board.transpileTo(len(definition_board.data.code))

        main.scope.add_functions(definition_main.scope.functions)
        board.scope.add_functions(definition_board.scope.functions)

        main.transpileTo(len(main.data.code))
        board.transpileTo(len(board.data.code))


    @staticmethod
    def get_code(self) -> list[str]:
        self.transpileTo(len(self.data.code))
        self.finish()

        return self.data.code_done

    @staticmethod
    def get_errors(code: list[str]) -> list[Error]:
        main, board, definition = Transpiler.get_transpiler(code)
        main.transpileTo(len(main.data.code))
        board.transpileTo(len(board.data.code))
        definition.transpileTo(len(definition.data.code))
        return main.data.errors + board.data.errors + definition.data.errors


if __name__ == '__main__':
    Transpiler = Transpiler(
        code=["int[][] x = [[1, 2, 3], [4, 5, 6]]", "int y = x[0][0]", "int z = x[1][2]", "int a = x[1][0]"],
        mode='main', line_offset=0)
    print(Transpiler.transpileTo(10))
    print(Transpiler.data.code_done)
    print([str(e) for e in Transpiler.data.errors])
