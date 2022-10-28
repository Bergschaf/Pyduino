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
        self.assertEqual(do_value("0"), ("0", "int"))
        self.assertEqual(do_value(" 0 "), ("0", "int"))
        self.assertEqual(do_value("0 "), ("0", "int"))

        self.assertEqual(do_value("2423"), ("2423", "int"))
        self.assertEqual(do_value("-2423"), ("-2423", "int"))
        self.assertEqual(do_value("+2423 "), ("+2423", "int"))

        # Floats
        self.assertEqual(do_value("0.0"), ("0.0", "float"))
        self.assertEqual(do_value(" 0.0 "), ("0.0", "float"))
        self.assertEqual(do_value("  0.0 "), ("0.0", "float"))

        self.assertEqual(do_value("23.42"), ("23.42", "float"))
        self.assertEqual(do_value("-23.42"), ("-23.42", "float"))

        self.assertEqual(do_value("235235."), ("235235.", "float"))

        # Booleans
        self.assertEqual(do_value("True"), ("true", "bool"))
        self.assertEqual(do_value("False"), ("false", "bool"))

        self.assertEqual(do_value("   True "), ("true", "bool"))

        # Variables
        intialize([])
        add_variable_to_scope("test", "int", 0)
        self.assertEqual(do_value("test"), ("test", "int"))

        with self.assertRaises(SyntaxError) as context:
            do_value("test2")
        self.assertEqual(str(context.exception), "Value 'test2' at line 0 is not defined")

        intialize([])
        with self.assertRaises(SyntaxError) as context:
            do_value("test")
        self.assertEqual(str(context.exception), "Value 'test' at line 0 is not defined")

        add_variable_to_scope("test", "int", 2)

        variables_arduino.currentLineIndex = 1
        with self.assertRaises(SyntaxError) as context:
            do_value("test")
        self.assertEqual(str(context.exception), "Value 'test' at line 1 is not defined")
        variables_arduino.currentLineIndex = 3
        self.assertEqual(do_value("test"), ("test", "int"))

    def test_variable_scope(self):
        intialize(["", "", ""])
        add_variable_to_scope("test", "int", 0)
        self.assertEqual(variable_in_scope("test", 1), ("test", "int"))

        with self.assertRaises(SyntaxError) as context:
            variable_in_scope("test", 4)
        self.assertEqual(str(context.exception), "Variable 'test' at line 4 is not defined")

        with self.assertRaises(SyntaxError) as context:
            variable_in_scope("test2", 1)
        self.assertEqual(str(context.exception), "Variable 'test2' at line 1 is not defined")

        intialize(["", "    ", "    ", ""])

        add_variable_to_scope("test", "int", 0)
        self.assertEqual(variable_in_scope("test", 1), ("test", "int"))

        add_variable_to_scope("test2", "int", 1)
        self.assertEqual(variable_in_scope("test2", 2), ("test2", "int"))
        with self.assertRaises(SyntaxError) as context:
            variable_in_scope("test2", 3)
        self.assertEqual(str(context.exception), "Variable 'test2' at line 3 is not defined")



if __name__ == '__main__':
    unittest.main()
