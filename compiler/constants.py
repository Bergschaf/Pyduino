FILENAME = "../testPyduino.pino"

DEFAULT_INDEX_LEVEL = 4  # spaces

CLOSING_BRACKETS = {"(": ")", "[": "]", "{": "}"}
BRACKETS = ["(", ")", "[", "]", "{", "}"]

VALID_NAME_END_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

PRIMITIVE_TYPES = ["int", "float", "char", "bool"]
PRIMITIVE_ARRAY_TYPES = ["int[]", "float[]", "char[]", "bool[]"]

NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
ARITHMETIC_OPERATORS = ["+", "-", "*", "/", "%"]
CONDITION_OPERATORS_LEN1 = ["<", ">"]
CONDITION_OPERATORS_LEN2 = ["==", "!=", "<=", ">=", "&&", "||"]

OPERATORS = ARITHMETIC_OPERATORS + CONDITION_OPERATORS_LEN1 + CONDITION_OPERATORS_LEN2

CONDITION_CONDITIONS = ["and", "or"]

WHITESPACE = '" "'
