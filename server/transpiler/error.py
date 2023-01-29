from utils import Range
class Error:
    def __init__(self, message:str, range:Range):
        self.message = message

        self.range = range

    def __str__(self):
        return f"{self.message} at line {self.range}"

