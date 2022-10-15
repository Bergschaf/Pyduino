import unittest
from utils_arduino import *
from intitializer_arduino import intialize

class TestUtilsArduino(unittest.TestCase):
    def test_reset_sys_variable(self):
        next_sys_variable()
        reset_sys_variable()
        self.assertEqual(variables_arduino.sysVariableIndex, 0)

    def test_next_sys_variable(self):
        self.assertEqual(next_sys_variable(), f"_sys_var_1")
        self.assertEqual(next_sys_variable(), f"_sys_var_2")
        self.assertEqual(next_sys_variable(), f"_sys_var_3")
        self.assertEqual(next_sys_variable(), f"_sys_var_4")

    def test_find_closing_bracket_in_value(self):
        # What if the bracket isn't a string of length 1?
        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("([(])", "test", 0)
        self.assertEqual(str(context.exception), "Bracket has to be a string of length 1")

        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("([(])", (), 0)
        self.assertEqual(str(context.exception), "Bracket has to be a string of length 1")

        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("([(])", [], 0)
        self.assertEqual(str(context.exception), "Bracket has to be a string of length 1")

        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("([(])", {}, 0)
        self.assertEqual(str(context.exception), "Bracket has to be a string of length 1")

        # What if the bracket isn't a valid opening bracket
        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("([(])", ")", 0)
        self.assertEqual(str(context.exception), "')' is not a valid opening bracket")

        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("([(])", "]", 0)
        self.assertEqual(str(context.exception), "']' is not a valid opening bracket")

        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("([(])", "}", 0)
        self.assertEqual(str(context.exception), "'}' is not a valid opening bracket")

        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("([(])", "t", 0)
        self.assertEqual(str(context.exception), "'t' is not a valid opening bracket")

        # What if the bracket isn't at the start col
        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("(1, 2, 3)", "(", 1)
        self.assertEqual(str(context.exception), "Value does not start with '('")

        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("()({[]}", "{", 2)
        self.assertEqual(str(context.exception), "Value does not start with '{'")

        with self.assertRaises(SyntaxError) as context:
            find_closing_bracket_in_value("([(])", "[", 0)
        self.assertEqual(str(context.exception), "Value does not start with '['")

        # Some Basic Tests
        self.assertEqual(find_closing_bracket_in_value("()", "(", 0), 1)
        self.assertEqual(find_closing_bracket_in_value("((()))", "(", 0), 5)
        self.assertEqual(find_closing_bracket_in_value("((()))", "(", 1), 4)
        self.assertEqual(find_closing_bracket_in_value("((()))", "(", 2), 3)

        self.assertEqual(find_closing_bracket_in_value("[]", "[", 0), 1)
        self.assertEqual(find_closing_bracket_in_value("[[]]", "[", 0), 3)
        self.assertEqual(find_closing_bracket_in_value("[[]]", "[", 1), 2)

        self.assertEqual(find_closing_bracket_in_value("{}", "{", 0), 1)
        self.assertEqual(find_closing_bracket_in_value("{{}}", "{", 0), 3)
        self.assertEqual(find_closing_bracket_in_value("{{}}", "{", 1), 2)

        self.assertEqual(find_closing_bracket_in_value("test(1,2,3)", "(", 4), 10)
        self.assertEqual(find_closing_bracket_in_value("test[2][3]", "[", 4), 6)
        self.assertEqual(find_closing_bracket_in_value("test[2][3]", "[", 7), 9)
        self.assertEqual(find_closing_bracket_in_value("test{2,3}", "{", 4), 8)

    def test_do_arguments(self):
        self.assertEqual(do_arguments("1,2,3"), ([("1", "int"), ("2", "int"), ("3", "int")], {}))

    def test_do_value(self):
        intialize([])

        self.assertEqual(do_value(""), ("", None))

        # Strings
        self.assertEqual(do_value('"test"'), ('"test"', "string"))
        self.assertEqual(do_value('  "test"  '), ('"test"', "string"))
        self.assertEqual(do_value('"test"  '), ('"test"', "string"))
        self.assertEqual(do_value('  "test"'), ('"test"', "string"))
        self.assertEqual(do_value('"  test"'), ('"  test"', "string"))
        self.assertEqual(do_value('"test  "'), ('"test  "', "string"))
        self.assertEqual(do_value(' "  te s t  " '), ('"  te s t  "', "string"))

        with self.assertRaises(SyntaxError) as context:
            do_value('"test')
        self.assertEqual(str(context.exception), "unterminated string literal \" at line '0'")

        with self.assertRaises(SyntaxError) as context:
            do_value(' " test ')
        self.assertEqual(str(context.exception), "unterminated string literal \" at line '0'")

        with self.assertRaises(SyntaxError) as context:
            do_value('test"')
        self.assertEqual(str(context.exception), "unterminated string literal \" at line '0'")

        with self.assertRaises(SyntaxError) as context:
            do_value('  test " ')
        self.assertEqual(str(context.exception), "unterminated string literal \" at line '0'")

        # Chars
        self.assertEqual(do_value("'t'"), ("'t'", "char"))
        self.assertEqual(do_value(" 't' "), ("'t'", "char"))
        self.assertEqual(do_value("'t' "), ("'t'", "char"))
        self.assertEqual(do_value(" 't'"), ("'t'", "char"))
        self.assertEqual(do_value("' '"), ("' '", "char"))
        self.assertEqual(do_value("'^'"), ("'^'", "char"))
        self.assertEqual(do_value("'a'"), ("'a'", "char"))

        with self.assertRaises(SyntaxError) as context:
            do_value("'")
        self.assertEqual(str(context.exception), "unterminated char literal ' at line '0'")

        with self.assertRaises(SyntaxError) as context:
            do_value(" t '")
        self.assertEqual(str(context.exception), "unterminated char literal ' at line '0'")

        with self.assertRaises(SyntaxError) as context:
            do_value("' t")
        self.assertEqual(str(context.exception), "unterminated char literal ' at line '0'")

        with self.assertRaises(SyntaxError) as context:
            do_value("'te'")
        self.assertEqual(str(context.exception), "''te'' at line '0' is not a valid character")

        with self.assertRaises(SyntaxError) as context:
            do_value("'t '")
        self.assertEqual(str(context.exception), "''t '' at line '0' is not a valid character")

        with self.assertRaises(SyntaxError) as context:
            do_value("' t'")
        self.assertEqual(str(context.exception), "'' t'' at line '0' is not a valid character")

        # Ints





if __name__ == '__main__':
    unittest.main()
