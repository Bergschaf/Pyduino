from data import Data
from fallbacks import *


class Position:
    def __init__(self, line, col):
        self.line = line
        self.col = col

    def __str__(self):
        return f"{self.line}:{self.col}"


class Range:
    def __init__(self, start_line, start_col, end_line=None, end_col=None, complete_line=False, data:Data=None):
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


class CurrentLocation:
    def __init__(self, code, indentations: list[int], line_offset=0,
                 default_StringNotFoundInRangeFallback: type(StringNotFound_Fallback) = None):
        self.code = code
        self.indentations = indentations  # list of indentation levels, 1 for each four spaces

        self.line_offset = line_offset

        self.default_StringNotFoundInRangeFallback: StringNotFound_Fallback = WholeLine if default_StringNotFoundInRangeFallback is None else default_StringNotFoundInRangeFallback
        # the method that will be used to produced a range (or an error) if the requested string is not found
        self.line = 0
        self.col = 0

    def next_line(self):
        self.line += 1
        self.col = self.indentations[self.line] * 4

    def getLine(self, with_indent=True) -> Range:
        """Returns a range object for the current line.
        If with_indent is True, the range will start at the first character of the line.
        If with_indent is False, the range will start at the first non-whitespace character of the line."""
        if with_indent:
            return Range(self.line + self.line_offset, 0, end_col=len(self.code[self.line]))
        else:
            return Range(self.line + self.line_offset, self.indentations[self.line] * 4,
                         end_col=len(self.code[self.line]))

    def getPosition(self) -> Position:
        """Returns a range object for the current position. (Might not be accurate)"""
        return Position(self.line + self.line_offset, self.col)

    def getString(self, string: str, spaces_around: bool = False, fallback:type[StringNotFound_Fallback]=None,
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
            fallback = self.default_StringNotFoundInRangeFallback

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
    def __init__(self, location: CurrentLocation, data: Data):
        self.data = data
        self.location = location

    def getIndentation(self, line: str, line_id: int) -> int:
        """Returns the indentation level of the given line.
        The indentation level is the number of four spaces at the start of the line.
        location_updated should be True if the current location has been updated to the start of the line.
        """
        indentation = len(line) - len(line.lstrip())
        if indentation % 4 != 0:
            self.location.getString(" " * indentation, fallback=WholeLineWithIndent, line=line_id,
                                    start_beginning=True)
        return indentation // 4

    def getIndentations(self, code: list[str]) -> list[int]:
        """Returns a list of indentation levels for each line in the given code.
        The indentation level is the number of four spaces at the start of the line."""
        indentations = []
        for i, line in enumerate(code):
            indentations.append(self.getIndentation(line, i))
        return indentations

    def findClosingBracket(self, bracket: str, pos: Position, fallback=Fallback.wholeLine()):
