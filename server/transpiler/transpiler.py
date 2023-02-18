from server.transpiler.scope import Scope
from server.transpiler.variable import *
from server.transpiler.control import Control
from server.transpiler.function import Function
from server.transpiler.tokenizer import *


class Transpiler:
    def __init__(self, code: list[str], mode="main", line_offset=0):
        """
        :param code: The Code to transpile (including the #main or #board)
        :param mode: main or board
        :param line_offset: The line offset of the code segment
        """
        self.mode = mode

        self.data: Data = Data(code, line_offset)
        self.location: CurrentLocation = CurrentLocation(code, self.data.indentations)

        self.utils: StringUtils = StringUtils(self.location, self.data, self)

        self.data.indentations = self.utils.getIndentations(self.data.code)
        self.location.indentations = self.data.indentations

        self.data.code_tokens = [Token.tokenize(line, Position(i, 0)) for i, line in enumerate(self.data.code)]
        self.data.enumerator = enumerate(self.data.code_tokens)

        self.scope: Scope = Scope(self.data, self.location)

        self.checks = [Variable.check_definition, Control.check_condition, Function.check_definition,
                       Function.check_return, Function.check_call]  # the functions to check for different instruction types

    def next_line(self):
        index, line = next(self.data.enumerator)
        self.location.next_line()
        self.do_line(line)

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


if __name__ == '__main__':
    Transpiler = Transpiler(
        code=["int x():","    int adf = 2", "    return 2","    return 2", "int y():", "    return 2","int z():", "    return x() + y()"],
        mode='main', line_offset=0)
    print(Transpiler.transpileTo(10))
    print(Transpiler.data.code_done)
    print([str(e) for e in Transpiler.data.errors])
