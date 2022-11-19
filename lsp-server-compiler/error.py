class Error:
    def __init__(self, message, line, column, end_line=None, end_column=None):
        self.message = message
        self.line = line + 1  # because the line is 0 indexed
        self.column = column
        self.end_line = end_line if end_line is not None else line
        self.end_column = end_column if end_column is not None else column

    def __str__(self):
        return f"{self.message} at line {self.line} - {self.end_line}, column {self.column} - {self.end_column}"
