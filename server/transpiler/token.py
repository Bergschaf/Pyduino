from pyduino_utils import *


class TokenType:
    def __init__(self, name):
        self.name = name


class Token:
    def __init__(self, type: TokenType, location: Range, value=None):
        self.type = type
        self.value = value
        self.location = location

    @staticmethod
    def tokenize(string: str, start: Position) -> list['Token']:
        bracket_levels = [0, 0, 0]
        last_space = start
        enumerator = enumerate(string)
        tokens = []
        for i, char in enumerator:
            if char in "([{":
                bracket_levels["([{".index(char)] += 1
            elif char in ")]}":
                bracket_levels[")]}".index(char)] -= 1

            if char == "\"":
                for j, char2 in enumerator:
                    if char2 == "\"":
                        break
                else:
                    break

            if char == " " and bracket_levels == [0, 0, 0]:
                tokens.append(
                    Token.get_token(string[last_space.col - start.col:i], Range.fromPositions(last_space, Position(start.line, start.col + i))))
                last_space = Position(start.line, start.col + i)
        tokens.append(Token.get_token(string[last_space.col:], Range.fromPositions(last_space, Position(start.line, start.col + len(string)))))

        return [t for t in tokens if t is not None]

    @staticmethod
    def get_token(string: str, range: Range) -> 'Token':
        if string == "":
            return None
        string = string.strip()
        if string in TOKENS.keys():
            return Token(TOKENS[string], range)

        if string[0] in "([":
            type = Brackets.ROUND if string[0] == "(" else Brackets.SQUARE
            return Brackets(type, range, Token.tokenize(string[1:-1], range.start.add_col(1)), string[-1] == string[0])

        if string.isnumeric():
            return Value(Value.NUMERIC_INT, range, string)

        if string.replace(".", "", 1).isnumeric() and "." in string:
            return Value(Value.NUMERIC_FLOAT, range, string)

        if StringUtils.is_identifier(string):
            return Value(Value.IDENTIFIER, range, string)

        return Value(Value.WORD, range, string)

    def __str__(self):
        return f"{self.type.name} {self.value} {self.location}"


class Operator(Token):
    def __init__(self, type: TokenType, location: Range, left: Token, right: Token, value=None):
        super().__init__(type, location, value)
        self.left = left
        self.right = right


class Math_Operator(Operator):
    PLUS = TokenType("+")
    MINUS = TokenType("-")
    MULTIPLY = TokenType("*")
    DIVIDE = TokenType("/")
    MODULO = TokenType("%")
    FLOOR_DIVIDE = TokenType("//")


class Compare_Operator(Operator):
    EQUAL = TokenType("==")
    NOT_EQUAL = TokenType("!=")
    GREATER = TokenType(">")
    GREATER_EQUAL = TokenType(">=")
    LESS = TokenType("<")
    LESS_EQUAL = TokenType("<=")


class Bool_Operator(Operator):
    AND = TokenType("and")
    OR = TokenType("or")
    NOT = TokenType("not")


class Value(Token):
    NUMERIC_FLOAT = TokenType("numeric_float")
    NUMERIC_INT = TokenType("numeric_int")
    IDENTIFIER = TokenType("identifier")
    WORD = TokenType("word")

    def __init__(self, type, range, value):
        super().__init__(type, range, value)


class Brackets(Token):
    ROUND = TokenType("()")
    SQUARE = TokenType("[]")

    def __init__(self, type, location: Range, inside: list[Token], closed: bool):
        super().__init__(type, location, None)
        self.closed = closed
        self.inside = inside


class Separator(Token):
    COMMA = TokenType(",")
    COLON = TokenType(":")


class Keyword(Token):
    IF = TokenType("if")
    ELSE = TokenType("else")
    ELIF = TokenType("elif")
    WHILE = TokenType("while")
    FOR = TokenType("for")
    IN = TokenType("in")
    RETURN = TokenType("return")
    BREAK = TokenType("break")
    CONTINUE = TokenType("continue")


class Primitive_Datatype(Token):
    INT = TokenType("int")
    FLOAT = TokenType("float")
    STRING = TokenType("string")
    BOOL = TokenType("bool")


class Derived_Datatype(Token):
    Array = TokenType("array")

    def __init__(self, type, location: Range, dimensions: int, datatype: Primitive_Datatype):
        super().__init__(type, location, None)
        self.dimensions = dimensions
        self.datatype = datatype


TOKENS = {
    "+": Math_Operator.PLUS,
    "-": Math_Operator.MINUS,
    "*": Math_Operator.MULTIPLY,
    "/": Math_Operator.DIVIDE,
    "%": Math_Operator.MODULO,
    "//": Math_Operator.FLOOR_DIVIDE,
    "==": Compare_Operator.EQUAL,
    "!=": Compare_Operator.NOT_EQUAL,
    ">": Compare_Operator.GREATER,
    ">=": Compare_Operator.GREATER_EQUAL,
    "<": Compare_Operator.LESS,
    "<=": Compare_Operator.LESS_EQUAL,
    "and": Bool_Operator.AND,
    "or": Bool_Operator.OR,
    "not": Bool_Operator.NOT,
    ",": Separator.COMMA,
    ":": Separator.COLON,
    "if": Keyword.IF,
    "else": Keyword.ELSE,
    "elif": Keyword.ELIF,
    "while": Keyword.WHILE,
    "for": Keyword.FOR,
    "in": Keyword.IN,
    "return": Keyword.RETURN,
    "break": Keyword.BREAK,
    "continue": Keyword.CONTINUE,
    "int": Primitive_Datatype.INT,
    "float": Primitive_Datatype.FLOAT,
    "str": Primitive_Datatype.STRING,
    "bool": Primitive_Datatype.BOOL
}

if __name__ == '__main__':
    print([str(t) for t in Token.tokenize("1 (+ 2) + 3", Position(0, 0))])
