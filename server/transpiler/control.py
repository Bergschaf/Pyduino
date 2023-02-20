from server.transpiler.pyduino_utils import *
from server.transpiler.variable import *


class Control:
    @staticmethod
    def check_condition(instuction: list[Token], transpiler: 'Transpiler'):
        """
        :return: True if the line is a control statement, False if not
        """
        if instuction[0].type == Keyword.IF:
            Control.do_if(instuction, transpiler)
            return True

    @staticmethod
    def do_condition(condition: list[Token], transpiler: 'Transpiler', condition_type: str):
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
            transpiler.data.newError(f"Condition of {condition_type} statement must be a boolean", Range.fromPositions(condition[0].location.start, condition[-1].location.end))
        return instruction.name

    @staticmethod
    def do_if(instruction: list[Token], transpiler: 'Transpiler'):

        location, data = transpiler.location, transpiler.data

        instruction = StringUtils.check_colon(instruction, transpiler)

        condition = Control.do_condition(instruction[1:], transpiler, "if")

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


            if line[0].type == Keyword.ELIF and data.indentations[index] == data.indentations[if_position]:

                instruction = StringUtils.check_colon(instruction, transpiler)

                condition = Control.do_condition(instruction[1:], transpiler, "elif")

                data.code_done.append(f"else if ({condition}) {{")

                end_line = StringUtils.get_indentation_range(index + 1, transpiler)

                transpiler.transpileTo(end_line)
                data.code_done.append("}")
            else:
                transpiler.do_line(line)
                break

        if line[0].type == Keyword.ELSE and data.indentations[index] == data.indentations[if_position]:
            StringUtils.check_colon(line, transpiler)
            data.code_done.append("else {")
            end_line = StringUtils.get_indentation_range(index + 1, transpiler)
            transpiler.transpileTo(end_line)
            data.code_done.append("}")
