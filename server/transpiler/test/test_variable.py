import unittest
from server.transpiler.transpiler import Transpiler
from server.transpiler.variable import Value


class TestValue(unittest.TestCase):
    def test_do_value(self):
        pairs = [
            ["4269", "4269"],
            ["3.141", "3.141"],
            ["True", "true"],
            ["False", "false"],
            ['"Hello World"', '"Hello World"'],
            ['[1,2,3]', '{1,2,3}'],
            ['[[[1,2,3],[4,5,6]],[[7,8,9],[10,11,12]]]', '{{{1,2,3},{4,5,6}},{{7,8,9},{10,11,12}}}'],
            ['[["Hello","World"],["Hello","World"]]', '{{"Hello","World"},{"Hello","World"}}'],

            # + operator
            ["41+69", "(41 + 69)"],
            ["1234 + 3.141", "((float)1234 + 3.141)"],
            ["3.141+123", "(3.141 + (float)123)"],
            ["222.22+333.333", "(222.22 + 333.333)"],
            ['2.2 + "3.3"', "(String(2.2) + \"3.3\")"],
            ['"Hello"+"World"', '("Hello" + "World")'],
            ['"Hello"+123', '("Hello" + String(123))'],
            ['"Hello"+3.141', '("Hello" + String(3.141))'],
            ['"Hello"+True', '("Hello" + String(true))'],
            ['"Hello"+False', '("Hello" + String(false))'],

            ["22222-333333333", "(22222 - 333333333)"],
            ["3.141-123", "(3.141 - (float)123)"],
            ["123-3.141", "((float)123 - 3.141)"],
            ["222.22-333.333", "(222.22 - 333.333)"],

            ["22222*33", "(22222 * 33)"],
            ["3.141*123", "(3.141 * (float)123)"],
            ["123*3.141", "((float)123 * 3.141)"],
            ["222.22*333.333", "(222.22 * 333.333)"],

            ["22222/33", "((float)22222 / (float)33)"],
            ["3.141/123", "(3.141 / (float)123)"],
            ["123/3.141", "((float)123 / 3.141)"],
            ["222.22/333.333", "(222.22 / 333.333)"],

            ["22222%33", "(22222 % 33)"]
        ]
        for pair in pairs:
            print("Testing: " + pair[0])
            transpiler = Transpiler([pair[0]])
            self.assertEqual(Value.do_value(pair[0], transpiler).name, pair[1])


if __name__ == '__main__':
    unittest.main()
