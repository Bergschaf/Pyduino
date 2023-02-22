from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import lsprotocol.types as lsp

if TYPE_CHECKING:
    from server.transpiler.transpiler import Transpiler
    from server.transpiler.function import Function
    from server.transpiler.tokenizer import *


class Position:
    def __init__(self, line, col):
        self.line = line
        self.col = col


    def distance(self, other: 'Position', data: 'Data'):
        return len(data.getCode(Range.fromPositions(self.smaller(other), self.bigger(other))))

    def add_line(self, offset: int):
        return Position(self.line + offset, self.col)

    def add_col(self, offset: int):
        return Position(self.line, self.col + offset)

    def bigger(self, other):
        if self.line > other.line:
            return self
        if self.line < other.line:
            return other
        if self.col > other.col:
            return self
        return other

    def smaller(self, other):
        if self.line < other.line:
            return self
        if self.line > other.line:
            return other
        if self.col < other.col:
            return self
        return other

    def is_bigger(self, other):
        if self.line > other.line:
            return True
        if self.line < other.line:
            return False
        if self.col >= other.col:
            return True
        return False

    def shift_to_end(self, data: 'Data'):
        # shifts the position to the end of the line
        return Position(self.line, len(data.code[self.line]))

    def __str__(self):
        return f"{self.line}:{self.col}"

    @staticmethod
    def last_char(data: 'Data', line: int):
        """
        Returns the last character of a line
        :param data:
        :param line:
        :return:
        """
        return Position(line, len(data.code[line]))


class Range:
    def __init__(self, start_line, start_col, end_line=None, end_col=None, complete_line=False,
                 data: 'Data' = None):
        """
        :param start_line:
        :param start_col:
        :param end_line:
        :param end_col:
        :param complete_line: The End position will be set to the end of the line
        :param data: required if complete_line is True
        """
        if complete_line:
            if data is None:
                raise ValueError("Data is required to complete line")
            end_col = len(data.code[end_line if end_line is not None else start_line])
        self.start = Position(start_line, start_col)
        self.end = Position(end_line if end_line is not None else start_line,
                            end_col if end_col is not None else start_col)

    def in_range(self, position: Position):
        if self.start.line < position.line < self.end.line:
            return True
        if self.start.line == position.line and self.start.col <= position.col:
            return True
        if self.end.line == position.line and self.end.col >= position.col:
            return True

    def __str__(self):
        return f"{self.start} - {self.end}"

    @staticmethod
    def fromPositions(pos1: Position, pos2: Position):
        return Range(pos1.line, pos1.col, pos2.line, pos2.col)

    @staticmethod
    def fromPosition(pos: Position):
        return Range(pos.line, pos.col, pos.line, pos.col)


class Error:
    def __init__(self, message: str, range: Range):
        self.message = message
        self.range = range

    def __repr__(self):
        return f"{self.message} at line {self.range}"

    def get_Diagnostic(self, transpiler: 'Transpiler'):
        return lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=self.range.start.line + transpiler.data.line_offset,
                                   character=self.range.start.col),
                end=lsp.Position(line=self.range.end.line + transpiler.data.line_offset, character=self.range.end.col),
            ),
            message=self.message,
            severity=lsp.DiagnosticSeverity.Error, # TODO THANK YOU GITHUB COPILOT
            source="pyduino",
        )


class InvalidLineError(Exception):
    pass


class EndOfFileError(Exception):
    pass


class StringNotFound_Fallback(ABC):
    """
    This is a fallback that is used when a string is not found in a range.
    """

    @staticmethod
    @abstractmethod
    def fallback(data: 'Data', range: Range, string: str, custom_message: str = None):
        pass


class StringNotFound_ErrorFirstLine(StringNotFound_Fallback):
    """
    This fallback will underline the first line of the range.
    """

    def fallback(data: 'Data', range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message, Range(range.start.line, 0, complete_line=True, data=data))


class StringNotFound_ErrorCompleteRange(StringNotFound_Fallback):
    """
    This fallback will underline the whole range.
    """

    def fallback(data: 'Data', range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message, range)


class StringNotFound_ErrorStart(StringNotFound_Fallback):
    """
    This fallback will underline the start position of the range.
    """

    def fallback(data: 'Data', range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message, Range(range.start.line, range.start.col, range.start.line,
                                     range.start.col + 1))


class StringNotFound_ErrorEnd(StringNotFound_Fallback):
    """
    This fallback will underline the end position of the range.
    """

    def fallback(data: 'Data', range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message,
                      Range(range.end.line, range.end.col - 1, range.end.line, range.end.col))


class StringNotFound_ThrowError(StringNotFound_Fallback):
    """
    This fallback will throw a SyntaxError.
    """

    def fallback(data: 'Data', range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        raise SyntaxError(message)


class StringNotFound_DoNothing(StringNotFound_Fallback):
    """
    This fallback will do nothing.
    """

    def fallback(data: 'Data', range: Range, string: str, custom_message: str = None):
        pass


class Range_Fallback(ABC):
    """
    What to do when a value is not found but a range has to be returned.
    """

    @staticmethod
    @abstractmethod
    def fallback(location: 'CurrentLocation'):
        pass


class Range_SingleChar(Range_Fallback):
    @staticmethod
    def fallback(location: 'CurrentLocation'):
        return Range(location.getCurrentPosition(), location.getCurrentPosition())


class Range_WholeLine(Range_Fallback):
    @staticmethod
    def fallback(location: 'CurrentLocation'):
        return location.getCurrentLineRange()


class Range_WholeLineWithIndent(Range_Fallback):
    @staticmethod
    def fallback(location: 'CurrentLocation'):
        return location.getCurrentLineRange(with_indent=True)


class Range_ThrowError(Range_Fallback):
    @staticmethod
    def fallback(location: 'CurrentLocation'):
        raise SyntaxError("Could not find string in line " + str(location.getCurrentPosition()))


class InvalidLine_Fallback():
    @staticmethod
    @abstractmethod
    def fallback(transpiler: 'Transpiler'):
        pass


class InvalidLine_ThrowError(InvalidLine_Fallback):
    @staticmethod
    def fallback(transpiler: 'Transpiler'):
        raise SyntaxError(f"Invalid line at {transpiler.location.line}: " + transpiler.location.getCurrentLine())


class InvalidLine_Skip(InvalidLine_Fallback):
    @staticmethod
    def fallback(transpiler: 'Transpiler'):
        print([str(e) for e in transpiler.data.errors])
        raise InvalidLineError()


class CurrentLocation:
    def __init__(self, code: list[str], indentations: list[int],
                 default_Range_Fallback: type(Range_Fallback) = Range_WholeLine):
        self.code = code
        self.indentations = indentations  # list of indentation levels, 1 for each four spaces

        self.default_Range_Fallback: type(Range_Fallback) = Range_WholeLine \
            if default_Range_Fallback is None else default_Range_Fallback
        # the method that will be used to produced a range (or an error) if the requested string is
        # not found but a range is required
        self.position = Position(-1, 0)
        self.range: Range = Range(0, 0, 0, 0)

        self.loop_level = 0

        self.last_line = len(code) - 1

    def next_line(self):
        self.position.line += 1
        if self.position.line >= len(self.code):
            raise EndOfFileError()
        self.position.col = self.indentations[self.position.line] * 4
        self.range = Range.fromPositions(self.position,
                                         Position(self.position.line, len(self.code[self.position.line]) - 1))

    def getCurrentLine(self):
        return self.code[self.position.line]

    def getPositionOffset(self, position: Position, offset: int, include_newline=False,
                          include_indentation=True) -> Position:
        """
        Returns a new position object with the offset applied.
        :param position:
        :param offset: The number of characters to move the position by
        :param include_newline: if True, a newline character will count as one character
        :param include_indentation: if False, the indentation of the line will be ignored (should be True for most cases)
        :return: """
        pos = 0
        position = Position(position.line, position.col)
        while pos < offset:
            pos += 1
            position.col += 1
            if position.col >= len(self.code[position.line]):
                if include_newline:
                    pos += 1
                if not include_indentation:
                    position.line += 1
                    position.col = self.indentations[position.line] * 4
                else:
                    position.line += 1
                    position.col = 0
        return position

    def getCurrentLineRange(self, with_indent=True) -> Range:
        """Returns a range object for the current line.
        If with_indent is True, the range will start at the first character of the line.
        If with_indent is False, the range will start at the first non-whitespace character of the line."""
        if with_indent:
            return Range(self.position.line, 0, end_col=len(self.code[self.position.line]))
        else:
            return Range(self.position.line, self.indentations[self.position.line] * 4,
                         end_col=len(self.code[self.position.line]))

    def getCurrentPosition(self) -> Position:
        """Returns a positon object for the current position. (Might not be accurate)"""
        return Position(self.position.line, self.position.col)

    def getCurrentRange(self) -> Range:
        """Returns a range object for the current position. (Might not be accurate)"""
        return Range(self.range.start.line, self.range.start.col, self.range.end.line, self.range.end.col)

    def getRangeFromString(self, string: str, spaces_around: bool = False,
                           fallback: type(Range_Fallback) = Range_WholeLine,
                           start_beginning: bool = False, line=None, col=None) -> Range:
        """
        space_around: If True, the string will be surrounded by whitespace.
        start_beginning: If True, the search will start at the beginning of the line.
        fallback: The method that will be used to produced a range (or an error) if the requested string is not found.
        line: The line to search in. If None, the current line will be used.
        col: The column to start the search at. If None, the current column will be used.

        Returns a range object for the first occurrence of the given string in the current line
        """
        if line is None:
            line = self.position.line
        if col is None:
            col = self.position.col

        if fallback is None:
            fallback = self.default_Range_Fallback

        if spaces_around:
            if start_beginning:
                pos = self.code[line].find(" " + string + " ")
            else:
                pos = self.code[line].find(" " + string + " ", col)
        else:
            if start_beginning:
                pos = self.code[line].find(string)
            else:
                pos = self.code[line].find(string, col)

        if pos == -1:
            return fallback.fallback(self)
        else:
            return Range(line, pos, end_col=pos + len(string))

    def getFullWordRange(self, position: Position, word: str = None,
                         fallback: type[Range_Fallback] = Range_SingleChar) -> Range:
        """
        Tries to find the range of a word at the position. If word is None, the range of the word at the given position will be returned.
        :param position: The beginning of the word
        :param word:
        :param fallback:
        :return:
        """
        if word is None:
            for i, w in enumerate(self.code[position.line][position.col:]):
                if w in " \t":
                    end = i
                    break
            else:
                end = len(self.code[position.line]) - 1

            for i, w in enumerate(self.code[position.line][:position.col:-1]):
                if w in " \t":
                    start = i
                    break
            else:
                start = 0
            return Range(position.line, position.col - start, end_col=position.col + end)
        else:
            if self.code[position.line][position.col:].startswith(word):
                return Range(position.line, position.col, end_col=position.col + len(word))
            self.position = position
            return fallback.fallback(self)

    def setCursorToString(self, string: str, spaces_around: bool = False):
        """
        :param string:
        :param spaces_around: True if the string should be surrounded by whitespace
        :return:
        """
        self.range = self.getRangeFromString(string, spaces_around, start_beginning=True)
        self.position.col = self.range.start.col


class StringUtils:
    def __init__(self, location: CurrentLocation, data: 'Data', transpiler: 'Transpiler'):
        self.transpiler = transpiler
        self.data: Data = data
        self.location: CurrentLocation = location

    def getIndentation(self, line: str, line_id: int) -> int:
        """Returns the indentation level of the given line.
        The indentation level is the number of four spaces at the start of the line.
        location_updated should be True if the current location has been updated to the start of the line.
        """
        indentation = len(line) - len(line.lstrip())
        if indentation % 4 != 0:
            self.data.newError("Invalid indentation", self.location.getCurrentLineRange())
        return indentation // 4

    def getIndentations(self, code: list[str], tokens: 'list[list[Token]]') -> list[int]:
        """Returns a list of indentation levels for each line in the given code.
        The indentation level is the number of four spaces at the start of the line."""
        indentations = []
        for token in tokens:
            indentations.append(self.getIndentation(code[token[0].location.start.line], token[0].location.start.line))

        return indentations

    def findClosingBracketInCode(self, bracket: str, pos: Position,
                                 fallback: type[StringNotFound_Fallback] = StringNotFound_ErrorFirstLine,
                                 invalid_line_fallback: type[InvalidLine_Fallback] = InvalidLine_Skip) -> Position:
        """
        Searches for the closing bracket of the given bracket in the complete code.
        :param bracket:
        :param pos:
        :param fallback:
        :return:
        """
        pass

    def findClosingBracketInLine(self, bracket: str, line: int, col: int = None,
                                 fallback: type[StringNotFound_Fallback] = StringNotFound_ErrorFirstLine,
                                 invalid_line_fallback: type[InvalidLine_Fallback] = InvalidLine_Skip) -> Position:
        """
        Searches for the closing bracket of the given bracket in the given line.
        :param bracket:
        :param line:
        :param col: start at this column
        :param fallback:
        :return:
        """
        if col is None:
            col = 0
        return self.findClosingBracketInRange(bracket, Range(line, col, complete_line=True),
                                              fallback)

    def findClosingBracketInRange(self, bracket: str, range: Range,
                                  error_fallback: type[StringNotFound_Fallback] = StringNotFound_ErrorCompleteRange,
                                  invalid_line_fallback: type[InvalidLine_Fallback] = InvalidLine_Skip) -> Position:
        """
        :param bracket:
        :param range:
        :param error_fallback: What error to raise (or show) if the closing bracket is not found.
        :param invalid_line_fallback: What to do when no closing bracket is found
        :return:
        """
        opening_brackets = "([{\""

        if bracket not in opening_brackets:
            raise ValueError(f"'{bracket}' Invalid opening bracket")
        if self.data.getCode(range.start) != bracket:
            raise ValueError(f"Range does not start with '{bracket}'")

        bracket_levels = [0] * 4  # 0: (), 1: [], 2: {}, 3: ""
        bracket_levels[opening_brackets.index(bracket)] += 1

        opening_brackets = "([{"
        closing_brackets = ")]}"

        code = self.data.getCode(range)

        enumerator = enumerate(code[1:])

        for i, char in enumerator:
            if char in opening_brackets:
                bracket_levels[opening_brackets.index(char)] += 1
            elif char in closing_brackets:
                bracket_levels[closing_brackets.index(char)] -= 1

            if char == '"':
                start = i
                try:
                    while next(enumerator)[1] != '"':
                        pass
                except StopIteration:
                    self.data.newError("Missing closing quotation mark", Range.fromPositions(
                        self.location.getPositionOffset(range.start, start),
                        self.location.getPositionOffset(range.start, len(code))))

            if all(x == 0 for x in bracket_levels):
                return self.location.getPositionOffset(range.start, i + 1)

        error_fallback.fallback(self.data, range, custom_message=f"No closing bracket found" \
                                                                 "for '{bracket}'", string=bracket)
        invalid_line_fallback.fallback(self.transpiler)

    def searchOutsideBrackets(self, value: str, range: Range,
                              fallback: type[
                                  StringNotFound_Fallback] = StringNotFound_ErrorCompleteRange) -> 'Position | bool':
        """
        Searches for the given value outside of brackets.
        """
        i = 0
        code = self.data.getCode(range)
        brackets = "([{\""
        while i < len(code):
            if code[i] in brackets:
                end_pos = self.findClosingBracketInRange(code[i], Range.fromPositions(
                    self.location.getPositionOffset(range.start, i), range.end))
                i = end_pos.distance(range.start, data=self.data)

            elif code[i:].startswith(value):
                return self.location.getPositionOffset(range.start, i)
            i += 1
        fallback.fallback(self.data, range, custom_message=f"Could not find '{value}' outside of brackets",
                          string=value)
        return False

    @staticmethod
    def is_identifier(value: str) -> bool:
        """
        :param value: The value to check
        :return: True if the value is an identifier, False if not
        """
        if value.isnumeric():
            return False
        for i in value:
            if not i.isalnum() and i != "_":
                return False
        return True

    @staticmethod
    def splitOutsideBrackets(value: str, separators: list[str], keep_separators: list = [],
                             split_after_brackets: bool = False) -> list[str]:
        """
        Splits a string by commas outside of brackets. Example:
        "a,v,[32,2,2],2(2,2),2" -> ["a,v", "[32,2,2]", "2(2,2)", "2"]
        :param split_after_brackets If true, the string will be split after each brakcet (that is on the outside) Example:
        "a,v,[32,(2,)2],2(2,2),2" -> ["a,v", "[32,(2,)2]", "2", "(2,2)", "2"]
        """
        bracket_levels = [0] * 3  # 0: (), 1: [], 2: {}
        result = []
        separators += keep_separators

        start = 0
        enumerator = enumerate(value)
        for i, char in enumerator:
            if char in "([{":
                bracket_levels["([{".index(char)] += 1
            elif char in ")]}":
                bracket_levels[")]}".index(char)] -= 1

            if char == '"':
                try:
                    while next(enumerator)[1] != '"':
                        pass
                except StopIteration:
                    pass
                    # TODO: Error

            if any(value[i:].startswith(x) for x in separators if len(x) > 1) and all(x == 0 for x in bracket_levels):
                separator = [x for x in separators if len(x) > 1 and value[i:].startswith(x)][0]
                result.append(value[start:i])
                if separator in keep_separators:
                    result.append(separator)
                start = i + len(separator)
                while i + 1 < start:
                    i, char = next(enumerator)

            elif char in separators and all(x == 0 for x in bracket_levels):

                result.append(value[start:i])
                if char in keep_separators:
                    result.append(char)
                start = i + 1

            elif split_after_brackets:
                if char in ")]}" and all(x == 0 for x in bracket_levels):
                    result.append(value[start:i + 1])
                    start = i + 1

            # multticharacter separators

        result.append(value[start:])
        result = [x for x in result if x != ""]
        return result

    @staticmethod
    def check_colon(line: "list[Token]", transpiler: 'Transpiler') -> 'list[Token]':
        # returns line without colon
        if len(line) == 0:
            return line

        from server.transpiler.tokenizer import Separator
        if line[-1].type != Separator.COLON:
            transpiler.data.newError("Expected ':'", line[-1].location)
            return line
        return line[:-1]

    @staticmethod
    def get_indentation_range(start_line: int, transpiler: 'Transpiler') -> int:
        """
        Returns the last line with the same indentation as the given line
        """
        if start_line >= len(transpiler.location.indentations):
            return start_line
        indent = transpiler.location.indentations[start_line]
        for i in range(transpiler.location.position.line + 1, len(transpiler.location.indentations)):
            if transpiler.location.indentations[i] < indent:
                end_line = i - 1
                break
        else:
            end_line = len(transpiler.location.indentations) - 1
        return end_line

    def get_arguments(self, line: list['Token']):
        """
        Returns the arguments of a function call or definition
        line with brackets
        :return arguments, keyword arguments (as tuples)
        """
        line = line.strip()[1:-1]

        if line == "":
            return [], []

        arguments = StringUtils.splitOutsideBrackets(line, [","])
        args, kwargs = [], []

        for arg in arguments:
            x = StringUtils.splitOutsideBrackets(arg, ["="], keep_separators=True)
            if len(x) == 1 and kwargs:
                self.data.newError("Positional argument after keyword argument", self.location.getRangeFromString(arg))
            elif len(x) == 1:
                args.append(x[0].strip())
            elif len(x) == 3:
                kwargs.append((x[0].strip(), x[2].strip()))
            else:
                self.data.newError("Invalid Argument (Contains '=')", self.location.getRangeFromString(arg))
        return args

    @staticmethod
    def next_sysvar():
        Data.sys_var_index += 1
        return f"_sysvar_{Data.sys_var_index}"


import server.transpiler.tokenizer as t


class Data:
    sys_var_index = 0

    def __init__(self, code: list[str], line_offset: int, strict_mode: bool = False):
        self.code: list[str] = code
        self.code_tokens: 'list[list[Token]]' = []
        self.line_offset: int = line_offset
        self.indentations: list[int] = []
        self.errors: list[Error] = []
        self.enumerator: enumerate = None
        self.code_done: list[str] = []
        self.invalid_line_fallback: type[InvalidLine_Fallback] = InvalidLine_Skip
        self.strict_mode: bool = strict_mode  # If true, the transpiler will stop on the first error
        self.in_function: Function = None
        self.current_decorator: str = None
        self.remote_function_count: int = 0 # the number of functions that can be called from the other platform
        self.remote_functions: list[Function] = [] # the functions that can be called from the other platform

        self.OPERATORS = [t.Math_Operator.PLUS, t.Math_Operator.MINUS, t.Math_Operator.MULTIPLY,
                          t.Math_Operator.DIVIDE, t.Math_Operator.MODULO, t.Compare_Operator.EQUAL,
                          t.Compare_Operator.NOT_EQUAL, t.Compare_Operator.LESS, t.Compare_Operator.GREATER,
                          t.Compare_Operator.GREATER_EQUAL, t.Compare_Operator.LESS_EQUAL, t.Bool_Operator.AND,
                          t.Bool_Operator.OR]
        self.OPERATION_ORDER = [[t.Math_Operator.MULTIPLY, t.Math_Operator.DIVIDE, t.Math_Operator.MODULO],
                                [t.Math_Operator.PLUS, t.Math_Operator.MINUS],
                                [t.Compare_Operator.EQUAL, t.Compare_Operator.NOT_EQUAL, t.Compare_Operator.LESS,
                                 t.Compare_Operator.GREATER, t.Compare_Operator.GREATER_EQUAL,
                                 t.Compare_Operator.LESS_EQUAL],
                                [t.Bool_Operator.AND], [t.Bool_Operator.OR]]
        self.VALID_NAME_END_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

    def newError(self, message: str, range: Range | Position):
        if type(range) is Position:
            range = Range.fromPosition(range)
        self.errors.append(Error(message, range))
        if self.strict_mode:
            raise SyntaxError(message)

    def getCode(self, location: 'Range | Position') -> str:
        # TODO newline option does not work
        if isinstance(location, Range):
            if location.start.line != location.end.line:
                return self.code[location.start.line][location.start.col:] + "".join(
                    self.code[location.start.line + 1:location.end.line]) + \
                    self.code[location.end.line][:location.end.col + 1]
            else:
                return self.code[location.start.line][location.start.col:location.end.col + 1]
        else:
            return self.code[location.line][location.col]
