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

            ["41+69", "(41 + 69)"],
            ["3.141+123", "(3.141 + (float)123)"],
            ['"Hello"+"World"', '"Hello" + "World"'],
            ['"Hello"+123', '"Hello" + String(123)'],
        ]
        for pair in pairs:
            transpiler = Transpiler([pair[0]])
            self.assertEqual(Value.do_value(pair[0], transpiler).name, pair[1])


if __name__ == '__main__':
    unittest.main()
