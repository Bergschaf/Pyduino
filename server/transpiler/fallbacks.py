from abc import ABC, abstractmethod
from server.transpiler.data import Data
from utils import Range, CurrentLocation


class StringNotFound_Fallback(ABC):
    @abstractmethod
    @staticmethod
    def fallback(location: CurrentLocation):
        pass


class StringNotFound_WholeLine(StringNotFound_Fallback):
    @staticmethod
    def fallback(location: CurrentLocation):
        return location.getLine()


class StringNotFound_WholeLineWithIndent(StringNotFound_Fallback):
    @staticmethod
    def fallback(location: CurrentLocation):
        return location.getLine(with_indent=True)


class StringNotFound_ThrowError(StringNotFound_Fallback):
    @staticmethod
    def fallback(location: CurrentLocation):
        raise SyntaxError("Could not find string in line " + str(location.getPosition()))


class StringNotFoundInRangeFallback(ABC):
    """
    This is a fallback that is used when a string is not found in a range.
    """

    @abstractmethod
    @staticmethod
    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        pass


class Range_ErrorFirstLine(StringNotFoundInRangeFallback):
    """
    This fallback will underline the first line of the range.
    """

    @staticmethod
    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message, Range(range.start.line, 0, complete_line=True, data=data))


class Range_ErrorCompleteRange(StringNotFoundInRangeFallback):
    """
    This fallback will underline the whole range.
    """

    @staticmethod
    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message, range)


class Range_ErrorStart(StringNotFoundInRangeFallback):
    """
    This fallback will underline the start position of the range.
    """
    @staticmethod
    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message, Range(range.start.line, range.start.col, range.start.line, range.start.col + 1))

class Range_ErrorEnd(StringNotFoundInRangeFallback):
    """
    This fallback will underline the end position of the range.
    """
    @staticmethod
    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        data.newError(message, Range(range.end.line, range.end.col - 1, range.end.line, range.end.col))

class Range_ThrowError(StringNotFoundInRangeFallback):
    """
    This fallback will throw a SyntaxError.
    """
    @staticmethod
    def fallback(data: Data, range: Range, string: str, custom_message: str = None):
        message = f"Could not find string '{string}' in range {range}" if custom_message is None else custom_message
        raise SyntaxError(message)
