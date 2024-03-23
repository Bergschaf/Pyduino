from server.transpiler.pyduino_utils import *


# AST here
class TokenType:
    def __init__(self, code, name):
        self.code = code
        self.name = name


class Token:
    def __init__(self, type: TokenType, location: Range, value=None):
        self.type = type
        self.value = value
        self.location = location

    @staticmethod
    def get_indentation(line: str):
        i = len(line) - len(line.lstrip())
        if i % 4 != 0:
            return i // 4 + 1
        return i // 4

    @staticmethod
    def tokenize_range(string: list[str], start: 'Position') -> 'Indent':
        indent = Indent(Range.fromPosition(start), [], None, 0)
        pos = start
        for i, line in enumerate(string):
            if line.strip() == "":
                continue
            pos = Position(start.line + i, 0)
            level = Token.get_indentation(line)
            if level > indent.level:
                indent = Indent(Range.fromPosition(pos), [], indent, level)
            elif level < indent.level:
                while indent.level > level:
                    indent.location.end = Position(pos.line - 1, len(string[i - 1]) - 1)
                    indent.parent.inside.append([indent])
                    indent.finish()
                    indent = indent.parent
            indent.inside.append(Token.tokenize(line, pos))

        while indent.level > 0:
            indent.location.end = Position(pos.line - 1, len(string[i - 1]) - 1)
            indent.parent.inside.append([indent])
            indent.finish()
            indent = indent.parent
        indent.finish()
        indent.location.end = Position(pos.line, len(string[i]) - 1)
        return indent

    @staticmethod
    def tokenize(string: str, start: 'Position') -> list['Token']:
        bracket_levels = [0, 0, 0]
        last_space = start
        last_bracket = start
        enumerator = enumerate(string)
        tokens = []
        for i, char in enumerator:
            if char in "([{":
                if bracket_levels == [0, 0, 0]:
                    last_bracket = Position(start.line, start.col + i)
                bracket_levels["([{".index(char)] += 1
            elif char in ")]}":
                bracket_levels[")]}".index(char)] -= 1
                if bracket_levels == [0, 0, 0]:
                    if last_space.col != last_bracket.col:
                        tokens.append(Token.get_token(string[last_space.col - start.col:last_bracket.col - start.col],
                                                      Range.fromPositions(last_space, last_bracket)))

                    tokens.append(Token.get_token(string[last_bracket.col - start.col:i + 1],
                                                  Range.fromPositions(last_bracket,
                                                                      Position(start.line, start.col + i + 1))))
                    last_space = Position(start.line, start.col + i + 1)
                    continue

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
    def get_token(string: str, range: 'Range') -> 'Token':

        range = Range.fromPositions(range.start.add_col(len(string) - len(string.lstrip())),
                                    range.end.add_col(-len(string) + len(string.rstrip())))
        string = string.strip()
        if string == "":
            return None

        if string in TOKENS.keys():
            t, cls = TOKENS[string]
            return cls(t, range, string)

        if string[0] in "([":
            type = Brackets.ROUND if string[0] == "(" else Brackets.SQUARE
            return Brackets(type, range, Token.tokenize(string[1:-1], range.start.add_col(1)), string[-1] == string[0])

        if string[0] == "@":
            return Decorator(Decorator.UNKNOWN, range, string[1:])

        if StringUtils.is_identifier(string):
            return Word(Word.IDENTIFIER, range, string)

        return Word(Word.VALUE, range, string)

    def __repr__(self):
        if self.type is Brackets.ROUND or self.type is Brackets.SQUARE:
            return f"{self.type.name} {[str(s) for s in self.inside]}  {self.location}"
        return f"{self.type.name}{f' {self.value} ' if self.value is not None else ''} ({self.location})"



class Indent(Token):
    INDENT = TokenType("INDENT", "INDENT")

    def __init__(self, location: Range, inside: list[list['Token']], parent: 'Indent', level=0):
        self.inside = inside
        self.parent = parent
        self.level = level
        self.enumerator = None
        self.index = 0
        self.variables = []
        super().__init__(self.INDENT, location, None)

    def finish(self):
        self.enumerator = enumerate(self.inside)

    def __repr__(self):
        return f"INDENT {self.level} {self.inside}"


class Operator(Token):
    def __init__(self, type: TokenType, location: Range, _, left=None, right=None):
        self.left = left
        self.right = right
        super().__init__(type, location, None)


class Math_Operator(Operator):
    PLUS = TokenType("+", "MATH_OPERATOR.PLUS")
    MINUS = TokenType("-", "MATH_OPERATOR.MINUS")
    MULTIPLY = TokenType("*", "MATH_OPERATOR.MULTIPLY")
    DIVIDE = TokenType("/", "MATH_OPERATOR.DIVIDE")
    MODULO = TokenType("%", "MATH_OPERATOR.MODULO")
    FLOOR_DIVIDE = TokenType("//", "MATH_OPERATOR.FLOOR_DIVIDE")


class Compare_Operator(Operator):
    EQUAL = TokenType("==", "Compare_Operator.EQUAL")
    NOT_EQUAL = TokenType("!=", "Compare_Operator.NOT_EQUAL")
    GREATER = TokenType(">", "Compare_Operator.GREATER")
    GREATER_EQUAL = TokenType(">=", "Compare_Operator.GREATER_EQUAL")
    LESS = TokenType("<", "Compare_Operator.LESS")
    LESS_EQUAL = TokenType("<=", "Compare_Operator.LESS_EQUAL")


class Bool_Operator(Operator):
    AND = TokenType("and", "Bool_Operator.AND")
    OR = TokenType("or", "Bool_Operator.OR")
    NOT = TokenType("not", "Bool_Operator.NOT")


class Word(Token):
    IDENTIFIER = TokenType("identifier", "Word.IDENTIFIER")
    VALUE = TokenType("value", "Word.VALUE")

    def __init__(self, type, range, value):
        super().__init__(type, range, value)


class Brackets(Token):
    ROUND = TokenType("()", "Brackets.ROUND")
    SQUARE = TokenType("[]", "Brackets.SQUARE")

    def __init__(self, type, location: Range, inside: list[Token], closed: bool):
        super().__init__(type, location, None)
        self.closed = closed
        self.inside = inside


class Separator(Token):
    COMMA = TokenType(",", "Separator.COMMA")
    COLON = TokenType(":", "Separator.COLON")
    SEMICOLON = TokenType(";", "Separator.SEMICOLON")
    HASHTAG = TokenType("#", "Separator.HASHTAG")
    ASSIGN = TokenType("=", "Separator.ASSIGN")


class Keyword(Token):
    IF = TokenType("if", "Keyword.IF")
    ELSE = TokenType("else", "Keyword.ELSE")
    ELIF = TokenType("elif", "Keyword.ELIF")
    WHILE = TokenType("while", "Keyword.WHILE")
    FOR = TokenType("for", "Keyword.FOR")
    IN = TokenType("in", "Keyword.IN")
    RETURN = TokenType("return", "Keyword.RETURN")
    BREAK = TokenType("break", "Keyword.BREAK")
    CONTINUE = TokenType("continue", "Keyword.CONTINUE")


class Datatype(Token):
    INT = TokenType("int", "Datatype.INT")
    FLOAT = TokenType("float", "Datatype.FLOAT")
    STRING = TokenType("str", "Datatype.STRING")
    BOOL = TokenType("bool", "Datatype.BOOL")
    VOID = TokenType("void", "Datatype.VOID")


class Decorator(Token):
    MAIN = TokenType("@main", "Decorator.MAIN")
    BOARD = TokenType("@board", "Decorator.BOARD")
    UNKNOWN = TokenType("@unknown", "Decorator.UNKNOWN")
    DECORATORS = [MAIN, BOARD, UNKNOWN]


NO_SPACE_TOKENS_LEN1 = ["+", "-", "*", "/", "%", ",", ":", "<", ">", "=", ";"]
NO_SPACE_TOKENS_LEN2 = ["==", ">=", "<=", "!=", "//"]
TOKENS = {
    "+": (Math_Operator.PLUS, Math_Operator),
    "-": (Math_Operator.MINUS, Math_Operator),
    "*": (Math_Operator.MULTIPLY, Math_Operator),
    "/": (Math_Operator.DIVIDE, Math_Operator),
    "%": (Math_Operator.MODULO, Math_Operator),
    "//": (Math_Operator.FLOOR_DIVIDE, Math_Operator),
    "==": (Compare_Operator.EQUAL, Compare_Operator),
    "!=": (Compare_Operator.NOT_EQUAL, Compare_Operator),
    ">": (Compare_Operator.GREATER, Compare_Operator),
    ">=": (Compare_Operator.GREATER_EQUAL, Compare_Operator),
    "<": (Compare_Operator.LESS, Compare_Operator),
    "<=": (Compare_Operator.LESS_EQUAL, Compare_Operator),
    "and": (Bool_Operator.AND, Bool_Operator),
    "or": (Bool_Operator.OR, Bool_Operator),
    "not": (Bool_Operator.NOT, Bool_Operator),
    ",": (Separator.COMMA, Separator),
    ":": (Separator.COLON, Separator),
    ";": (Separator.SEMICOLON, Separator),
    "#": (Separator.HASHTAG, Separator),
    "=": (Separator.ASSIGN, Separator),
    "if": (Keyword.IF, Keyword),
    "else": (Keyword.ELSE, Keyword),
    "elif": (Keyword.ELIF, Keyword),
    "while": (Keyword.WHILE, Keyword),
    "for": (Keyword.FOR, Keyword),
    "in": (Keyword.IN, Keyword),
    "return": (Keyword.RETURN, Keyword),
    "break": (Keyword.BREAK, Keyword),
    "continue": (Keyword.CONTINUE, Keyword),
    "int": (Datatype.INT, Datatype),
    "float": (Datatype.FLOAT, Datatype),
    "str": (Datatype.STRING, Datatype),
    "bool": (Datatype.BOOL, Datatype),
    "void": (Datatype.VOID, Datatype),
    "@main": (Decorator.MAIN, Decorator),
    "@board": (Decorator.BOARD, Decorator)
}

if __name__ == '__main__':
    print(Token.tokenize_range(["int x = (42 + 2) * 3", "    int x = 0"], Position(0, 0)))
