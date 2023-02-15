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

            if bracket_levels != [0, 0, 0]:
                continue

            if any(string[i:i + 2] == t for t in NO_SPACE_TOKENS_LEN2):
                tokens.append(
                    Token.get_token(string[last_space.col - start.col:i],
                                    Range.fromPositions(last_space, Position(start.line, start.col + i))))
                last_space = Position(start.line, start.col + i)

                tokens.append(Token.get_token(string[i:i + 2], Range.fromPositions(last_space, last_space.add_col(2))))
                next(enumerator)
                last_space = last_space.add_col(2)

            elif char == " " or any(char == t for t in NO_SPACE_TOKENS_LEN1):
                tokens.append(Token.get_token(string[last_space.col - start.col:i],
                                              Range.fromPositions(last_space, Position(start.line, start.col + i))))
                last_space = Position(start.line, start.col + i)

                if char == " ":
                    continue

                tokens.append(Token.get_token(char, Range.fromPositions(last_space, last_space.add_col(1))))
                last_space = last_space.add_col(1)

        tokens.append(Token.get_token(string[last_space.col - start.col:],
                                      Range.fromPositions(last_space, Position(start.line, start.col + len(string)))))

        return [t for t in tokens if t is not None]

    @staticmethod
    def is_token(value):
        return isinstance(value, Token)

    @staticmethod
    def get_token(string: str, range: Range) -> 'Token':

        range = Range.fromPositions(range.start.add_col(len(string) - len(string.lstrip())),
                                    range.end.add_col(-len(string) + len(string.rstrip())))
        string = string.strip()
        if string == "":
            return None
        if string in TOKENS.keys():
            return Token(TOKENS[string], range)

        if string[0] in "([":
            type = Brackets.ROUND if string[0] == "(" else Brackets.SQUARE
            return Brackets(type, range, Token.tokenize(string[1:-1], range.start.add_col(1)), string[-1] == string[0])

        if StringUtils.is_identifier(string):
            return Word(Word.IDENTIFIER, range, string)

        return Word(Word.VALUE, range, string)

    def __repr__(self):
        if self.type is Brackets.ROUND or self.type is Brackets.SQUARE:
            return f"{self.type.name} [{[str(s) for s in self.inside]}]  {self.location}"
        return f"{self.type.name} {self.value if self.value is not None else ''} {self.location}"


class Operator(Token):
    def __init__(self, type: TokenType, location: Range, _):
        super().__init__(type, location, None)


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


class Word(Token):
    IDENTIFIER = TokenType("identifier")
    VALUE = TokenType("value")

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
    SEMICOLON = TokenType(";")
    HASHTAG = TokenType("#")
    ASSIGN = TokenType("=")


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


class Datatype(Token):
    INT = TokenType("int")
    FLOAT = TokenType("float")
    STRING = TokenType("str")
    BOOL = TokenType("bool")
    VOID = TokenType("void")



NO_SPACE_TOKENS_LEN1 = ["+", "-", "*", "/", "%", ",", ":", "<", ">", "=", ":"]
NO_SPACE_TOKENS_LEN2 = ["==", ">=", "<=", "!=", "//"]
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
    "#": Separator.HASHTAG,
    "=": Separator.ASSIGN,
    "if": Keyword.IF,
    "else": Keyword.ELSE,
    "elif": Keyword.ELIF,
    "while": Keyword.WHILE,
    "for": Keyword.FOR,
    "in": Keyword.IN,
    "return": Keyword.RETURN,
    "break": Keyword.BREAK,
    "continue": Keyword.CONTINUE,
    "int": Datatype.INT,
    "float": Datatype.FLOAT,
    "str": Datatype.STRING,
    "bool": Datatype.BOOL,
    "void": Datatype.VOID,
}

if __name__ == '__main__':
    word = Word(Word.WORD, Range(Position(0, 0), Position(0, 4)), "test")
    print(Token.is_token(word))
