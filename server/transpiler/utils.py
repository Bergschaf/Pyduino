class Range:
    def __init__(self, start_line, start_col, end_line=None, end_col=None):
        self.start_line = start_line
        self.start_col = start_col
        self.end_line = start_line if end_line is None else end_line
        self.end_col = start_col if end_col is None else end_col

    def __str__(self):
        return f"{self.start_line}:{self.start_col} - {self.end_line}:{self.end_col}"


class CurrentLocation:
    Instance = None

    def __init__(self, code, indentations: list[int], line_offset=0, default_fallback=None):
        CurrentLocation.Instance = self
        self.code = code
        self.indentations = indentations  # list of indentation levels, 1 for each four spaces

        self.line_offset = line_offset

        self.default_fallback = Fallback.wholeLineWithIndent if default_fallback is None else default_fallback
        # the method that will be used to produced a range (or an error) if the requested string is not found

        self.line = 0
        self.col = 0

    def next_line(self):
        self.line += 1
        self.col = self.indentations[self.line] * 4

    def getLine(self, with_indent=True):
        """Returns a range object for the current line.
        If with_indent is True, the range will start at the first character of the line.
        If with_indent is False, the range will start at the first non-whitespace character of the line."""
        if with_indent:
            return Range(self.line + self.line_offset, 0, end_col=len(self.code[self.line]))
        else:
            return Range(self.line + self.line_offset, self.indentations[self.line] * 4,
                         end_col=len(self.code[self.line]))

    def getPosition(self):
        """Returns a range object for the current position. (Might not be accurate)"""
        return Range(self.line + self.line_offset, self.col)

    def getString(self, string: str, spaces_around: bool = False, fallback=None,
                  start_beginning: bool = False, line=None,col=None):
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
            fallback = self.default_fallback

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
            return fallback(self)
        else:
            return Range(line + self.line_offset, pos, end_col=pos + len(string))


class Fallback:
    @staticmethod
    def wholeLine(location: CurrentLocation):
        return location.getLine()

    @staticmethod
    def wholeLineWithIndent(location: CurrentLocation):
        return location.getLine(with_indent=True)

    @staticmethod
    def throwError(location: CurrentLocation):
        raise SyntaxError("Could not find string in line " + str(location.getPosition()))


class StringUtils:
    @staticmethod
    def getIndentation(line: str, location:CurrentLocation, line_id:int) -> int:
        """Returns the indentation level of the given line.
        The indentation level is the number of four spaces at the start of the line.
        location_updated should be True if the current location has been updated to the start of the line.
        """
        indentation = len(line) - len(line.lstrip())
        if indentation % 4 != 0:
            location.getString(" " * indentation, fallback=Fallback.throwError, line=line_id, start_beginning=True)
        return indentation // 4


    @staticmethod
    def getIndentations(code: list[str]):
        """Returns a list of indentation levels for each line in the given code.
        The indentation level is the number of four spaces at the start of the line."""
        indentations = []
        for line in code:
            indentations.append(StringUtils.getIndentation(line))
        return indentations

    @staticmethod
