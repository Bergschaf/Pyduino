from abc import ABC, abstractmethod


class Position:
    def __init__(self, line, col):
        self.line = line
        self.col = col

    def __str__(self):
        return f"{self.line}:{self.col}"


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
            end_col = len(data.code[start_line])
        self.start = Position(start_line, start_col)
        self.end = Position(end_line if end_line is not None else start_line,
                            end_col if end_col is not None else start_col)

    def __str__(self):
        return f"{self.start} - {self.end}"

    @staticmethod
    def fromPositions(pos1: Position, pos2: Position):
        return Range(pos1.line, pos1.col, pos2.line, pos2.col)


class Error:
    def __init__(self, message: str, range: Range):
        self.message = message
        self.range = range

    def __str__(self):
        return f"{self.message} at line {self.range}"


class Data:
    def __init__(self, code: list[str], line_offset: int):
        self.code: list[str] = code
        self.line_offset: int = line_offset
        self.indentations: list[int] = []
        self.errors: list[Error] = []
        self.enumerator:enumerate = enumerate(code)

    def newError(self, message: str, range: Range):
        self.errors.append(Error(message, range))

    def getCode(self, location: Range | Position, newline=True) -> str:
        if isinstance(location, Range):
            if newline:
                return self.code[location.start.line][location.start.col:] + "\n".join(
                    self.code[location.start.line + 1:location.end.line]) + "\n" + \
                       self.code[location.end.line][:location.end.col]
        else:
            return self.code[location.line][location.col]


class StringNotFound_Fallback(ABC):
    """
    This is a fallback that is used when a string is not found in a range.
    """

    @staticmethod
    @abstractmethod
    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        pass


class StringNotFound_ErrorFirstLine(StringNotFound_Fallback):
    """
    This fallback will underline the first line of the range.
    """

    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message, Range(range.start.line, 0, complete_line=True, data=data))


class StringNotFound_ErrorCompleteRange(StringNotFound_Fallback):
    """
    This fallback will underline the whole range.
    """

    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message, range)


class StringNotFound_ErrorStart(StringNotFound_Fallback):
    """
    This fallback will underline the start position of the range.
    """

    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message, Range(range.start.line, range.start.col, range.start.line,
                                     range.start.col + 1))


class StringNotFound_ErrorEnd(StringNotFound_Fallback):
    """
    This fallback will underline the end position of the range.
    """

    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message,
                      Range(range.end.line, range.end.col - 1, range.end.line, range.end.col))


class StringNotFound_ThrowError(StringNotFound_Fallback):
    """
    This fallback will throw a SyntaxError.
    """

    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        raise SyntaxError(message)


class Range_Fallback(ABC):
    """
    What to do when a value is not found but a range has to be returned.
    """

    @staticmethod
    @abstractmethod
    def fallback(location: 'CurrentLocation'):
        pass


class Range_WholeLine(Range_Fallback):
    def fallback(location: 'CurrentLocation'):
        return location.getLine()


class Range_WholeLineWithIndent(Range_Fallback):
    def fallback(location: 'CurrentLocation'):
        return location.getLine(with_indent=True)


class Range_ThrowError(Range_Fallback):
    def fallback(location: 'CurrentLocation'):
        raise SyntaxError("Could not find string in line " + str(location.getPosition()))


class InvalidLine_Fallback():
    @staticmethod
    @abstractmethod
    def fallback(transpiler: 'Transpiler', line: str, location: 'CurrentLocation'):
        pass


class CurrentLocation:
    def __init__(self, code: list[str], indentations: list[int], line_offset: int = 0,
                 default_Range_Fallback: type(Range_Fallback) = None):
        self.code = code
        self.indentations = indentations  # list of indentation levels, 1 for each four spaces

        self.line_offset = line_offset

        self.default_Range_Fallback: type(Range_Fallback) = Range_WholeLine \
            if default_Range_Fallback is None else default_Range_Fallback
        # the method that will be used to produced a range (or an error) if the requested string is
        # not found but a range is required
        self.line = 0
        self.col = 0

    def next_line(self):
        self.line += 1
        self.col = self.indentations[self.line] * 4

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
            if position.col >= len(self.code[position.line - self.line_offset]):
                if include_newline:
                    pos += 1
                if not include_indentation:
                    position.line += 1
                    position.col = self.indentations[position.line - self.line_offset] * 4
                else:
                    position.line += 1
                    position.col = 0
        return position

    def getCurrentLineRange(self, with_indent=True) -> Range:
        """Returns a range object for the current line.
        If with_indent is True, the range will start at the first character of the line.
        If with_indent is False, the range will start at the first non-whitespace character of the line."""
        if with_indent:
            return Range(self.line + self.line_offset, 0, end_col=len(self.code[self.line]))
        else:
            return Range(self.line + self.line_offset, self.indentations[self.line] * 4,
                         end_col=len(self.code[self.line]))

    def getCurrentPosition(self) -> Position:
        """Returns a positon object for the current position. (Might not be accurate)"""
        return Position(self.line + self.line_offset, self.col)

    def getRangeFromString(self, string: str, spaces_around: bool = False,
                           fallback: type(Range_Fallback) = None,
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
            line = self.line
        if col is None:
            col = self.col

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
            return Range(line + self.line_offset, pos, end_col=pos + len(string))


class StringUtils:
    def __init__(self, location: CurrentLocation, data: 'Data'):
        self.data = data
        self.location = location

    def getIndentation(self, line: str, line_id: int) -> int:
        """Returns the indentation level of the given line.
        The indentation level is the number of four spaces at the start of the line.
        location_updated should be True if the current location has been updated to the start of the line.
        """
        indentation = len(line) - len(line.lstrip())
        if indentation % 4 != 0:
            self.data.newError("Invalid indentation", self.location.getCurrentLineRange())
        return indentation // 4

    def getIndentations(self, code: list[str]) -> list[int]:
        """Returns a list of indentation levels for each line in the given code.
        The indentation level is the number of four spaces at the start of the line."""
        indentations = []
        for i, line in enumerate(code):
            indentations.append(self.getIndentation(line, i))

        return indentations

    def findClosingBracketInCode(self, bracket: str, pos: Position,
                                 fallback: type[
                                     StringNotFound_Fallback] = StringNotFound_ErrorFirstLine) -> Position:
        """
        Searches for the closing bracket of the given bracket in the complete code.
        :param bracket:
        :param pos:
        :param fallback:
        :return:
        """
        pass

    def findClosingBracketInLine(self, bracket: str, line: int, col:int = None,
                                 fallback: type[
                                     StringNotFound_Fallback] = StringNotFound_ErrorFirstLine) -> Position:
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
        return self.findClosingBracketInRange(bracket, Range(line, col, complete_line=True), fallback)

    def findClosingBracketInRange(self, bracket: str, range: Range, error_fallback: type[
        StringNotFound_Fallback] = StringNotFound_ErrorCompleteRange) -> Position:
        opening_brackets = "([{\""

        if bracket not in opening_brackets:
            raise ValueError(f"'{bracket}' Invalid opening bracket")
        if self.data.getCode(range.start) != bracket:
            raise ValueError(f"Range does not start with '{bracket}'")

        bracket_levels = [0] * 4  # 0: (), 1: [], 2: {}, 3: ""
        bracket_levels[opening_brackets.index(bracket)] += 1

        opening_brackets = "([{"
        closing_brackets = ")]}"

        code = self.data.getCode(range, newline=False)

        enumerator = enumerate(code)

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
                return self.location.getPositionOffset(range.start, i)

        error_fallback.fallback(self.data, range, custom_message=f"No closing bracket found" \
                                                           "for '{bracket}'", string=bracket)
