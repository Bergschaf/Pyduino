from error import Error
from utils import Range


class Data:
    def __init__(self, code: list[str], line_offset: int):
        self.code:list[str] = code
        self.line_offset:int = line_offset
        self.indentations:list[int] = []
        self.errors:list[Error] = []

    def newError(self, message: str, range: Range):
        self.errors.append(Error(message, range))
