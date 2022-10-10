import unittest
from utils_arduino import *


class TestUtilsArduino(unittest.TestCase):
    def test_reset_sys_variable(self):
        next_sys_variable()
        reset_sys_variable()
        self.assertEqual(variables_arduino.sysVariableIndex, 0)

    def test_next_sys_variable(self):
        self.assertEqual(next_sys_variable(), f"_sys_var_{324987 * 1}")
        self.assertEqual(next_sys_variable(), f"_sys_var_{324987 * 2}")
        self.assertEqual(next_sys_variable(), f"_sys_var_{324987 * 3}")
        self.assertEqual(next_sys_variable(), f"_sys_var_{324987 * 4}")

    def test_find_closing_bracket_in_value(self):
        # What if the bracket isn't at the start col
        self.failUnlessRaises(SyntaxError, find_closing_bracket_in_value, "[({})]", "(", 0, )
        # TODO https://www.geeksforgeeks.org/test-if-a-function-throws-an-exception-in-python/


        # Some Basic Tests
        self.assertEqual(find_closing_bracket_in_value("()", "(", 0), 1)
        self.assertEqual(find_closing_bracket_in_value("((()))", "(", 0), 5)
        self.assertEqual(find_closing_bracket_in_value("((()))", "(", 1), 4)
        self.assertEqual(find_closing_bracket_in_value("((()))", "(", 2), 3)


if __name__ == '__main__':
    unittest.main()
