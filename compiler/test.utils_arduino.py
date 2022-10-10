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


if __name__ == '__main__':
    unittest.main()
