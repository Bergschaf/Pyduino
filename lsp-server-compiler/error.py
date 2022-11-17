class Error:
    def __init__(self, message, line, column, end_line=None, end_column=None):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f"{self.message} at line {self.line}, column {self.column}"
