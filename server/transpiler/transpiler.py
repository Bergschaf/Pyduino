from server.transpiler.scope import Scope
from server.transpiler.variable import *
from server.transpiler.control import Control
from server.transpiler.function import Function


class Transpiler:
    def __init__(self, code: list[str], mode='main', line_offset=0):
        """
        :param code: The Code to transpile (including the #main or #board)
        :param mode: main or board
        :param line_offset: The line offset of the code segment
        """
        self.data: Data = Data(code, line_offset)
        self.location: CurrentLocation = CurrentLocation(code, self.data.indentations)

        self.utils: StringUtils = StringUtils(self.location, self.data, self)

        self.data.indentations = self.utils.getIndentations(self.data.code)
        self.location.indentations = self.data.indentations

        self.scope: Scope = Scope(self.data, self.location)

        self.checks = [Variable.check_definition, Control.check_condition, Function.check_definition,
                       Function.checK_return]  # the functions to check for different instruction types

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

    def do_line(self, line: str):
        instruction = line.strip()
        if "#" in instruction:
            instruction = instruction.split("#")[0].strip()
        if instruction == "":
            return
        if instruction.endswith(";"):
            instruction = instruction[:-1]
            # error on the semicolon
            pos = Position(self.location.position.line, len(
                self.data.code[self.location.position.line]))
            self.data.newError("We don't do that here", Range.fromPositions(pos, pos))

        for check in self.checks:
            if check(instruction, self):
                return

    def finish(self):
        """
        TODO add String function here in the c++ version:
        std::string String(int value) { return std::to_string(value); }
        std::string String(float value) { return std::to_string(value); }
        for all datatypes

        :return:
        """


if __name__ == '__main__':
    Transpiler = Transpiler(code=['int f():', '    return'], mode='main', line_offset=0)
    Transpiler.transpileTo(2)
    print(Transpiler.data.code_done)
    print([str(e) for e in Transpiler.data.errors])
