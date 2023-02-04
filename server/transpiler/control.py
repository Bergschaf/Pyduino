from server.transpiler.pyduino_utils import *
from server.transpiler.variable import *


class Control:
    @staticmethod
    def check_condition(instuction: str, transpiler: 'Transpiler'):
        """
        :param line:
        :param transpiler:
        :return: True if the line is a control statement, False if not
        """
        if instuction.startswith("if "):
            Control.do_if(instuction, transpiler)
            return True

    @staticmethod
    def do_condition(condition: str, transpiler: 'Transpiler', condition_type: str):
        """
        returns the c code for the control statement
        :param condition: the condition of the control statement
        :param transpiler:
        :param condition_type: if, while or for...
        :return:
        """
        instruction = Value.do_value(condition, transpiler)

        possible, instruction = instruction.type.to_bool()

        if not possible:
            transpiler.data.newError(f"Invalid condition for the {condition_type}-statement: " + instruction,
                                     Range.fromPositions(transpiler.location.position,
                                                         Position.last_char(transpiler.data, transpiler.location.position.line)))

        return instruction.name

    @staticmethod
    def do_if(instruction: str, transpiler: 'Transpiler'):

        """
        :param instruction: The instruction to transpile
        :param data: The data object
        :param location: The location object
        """
        location, data, utils = transpiler.location, transpiler.data, transpiler.utils

        instruction = StringUtils.check_colon(instruction, transpiler)[2:]

        condition = Control.do_condition(instruction, transpiler, "if")

        data.code_done.append(f"if ({condition}) {{")

        # Get the lentgh of the if-statement (identent part)
        if_position = location.position.line  # the position of the if-statement
        end_line = StringUtils.get_indentation_range(if_position + 1, transpiler)

        transpiler.transpileTo(end_line)

        data.code_done.append("}")

        while True:

            if location.position.line == location.last_line:
                return
            location.next_line()
            index, line = next(data.enumerator)

            if line.strip().startswith("elif") and data.indentations[index] == data.indentations[if_position]:
                instruction = line.strip()

                instruction = StringUtils.check_colon(instruction, transpiler)[4:]

                condition = Control.do_condition(instruction, transpiler, "elif")

                data.code_done.append(f"else if ({condition}) {{")

                end_line = StringUtils.get_indentation_range(index + 1, transpiler)

                transpiler.transpileTo(end_line)
                data.code_done.append("}")
            else:
                transpiler.do_line(line)
                break

        if line.strip().startswith("else") and data.indentations[index] == data.indentations[if_position]:
            data.code_done.append("else {")
            end_line = StringUtils.get_indentation_range(index + 1, transpiler)
            transpiler.transpileTo(end_line)
            data.code_done.append("}")
