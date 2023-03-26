import time

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
        elif instuction[0].type == Keyword.FOR:
            Control.do_for(instuction, transpiler)
            return True
        elif instuction[0].type == Keyword.WHILE:
            Control.do_while(instuction, transpiler)
            return True
        return False

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
            transpiler.data.newError(f"Condition of {condition_type} statement must be a boolean",
                                     Range.fromPositions(condition[0].location.start, condition[-1].location.end))
        return instruction.name

    @staticmethod
    def check_indent(transpiler: 'Transpiler', condition_type: str):
        if transpiler.current_indent.index + 1 >= len(transpiler.current_indent.inside):
            transpiler.data.newError(f"Expected indent after {condition_type} statement",
                                     Range.fromPositions(transpiler.current_indent.inside[-1][-1].location.start,
                                                         transpiler.current_indent.inside[-1][-1].location.end))
            return

        next_line = transpiler.current_indent.inside[transpiler.current_indent.index + 1]

        if next_line[0].type != Indent.INDENT:
            transpiler.data.newError(f"Expected indent after {condition_type} statement",
                                     Range.fromPositions(next_line[0].location.start, next_line[0].location.end))
        next(transpiler.current_indent.enumerator)
        transpiler.transpileRange(next_line[0])

    @staticmethod
    def do_if(instruction: list[Token], transpiler: 'Transpiler'):

        data = transpiler.data

        instruction = StringUtils.check_colon(instruction, transpiler)

        condition = Control.do_condition(instruction[1:], transpiler, "if")


        data.code_done.append(f"if ({condition}) {{")


        # Get the lentgh of the if-statement (identent part)
        Control.check_indent(transpiler, "if")

        data.code_done.append("}")

        while True:
            transpiler.current_indent = transpiler.current_indent.parent
            index, line = next(transpiler.current_indent.enumerator)
            transpiler.current_indent.index = index

            if line[0].type == Keyword.ELIF:

                instruction = StringUtils.check_colon(line, transpiler)

                condition = Control.do_condition(instruction[1:], transpiler, "elif")

                data.code_done.append(f"else if ({condition}) {{")

                Control.check_indent(transpiler, "elif")

                data.code_done.append("}")
            else:
                break

        if line[0].type == Keyword.ELSE:
            StringUtils.check_colon(line, transpiler)
            data.code_done.append("else {")

            Control.check_indent(transpiler, "else")

            data.code_done.append("}")
        else:
            transpiler.do_line(line)

        return True

    @staticmethod
    def do_while(instruction: list[Token], transpiler: 'Transpiler'):
        instruction = StringUtils.check_colon(instruction, transpiler)

        condition = Control.do_condition(instruction[1:], transpiler, "while")

        transpiler.data.code_done.append(f"while ({condition}) {{")

        transpiler.data.in_loop += 1
        Control.check_indent(transpiler, "while")
        transpiler.data.in_loop -= 1

        transpiler.data.code_done.append("}")

    @staticmethod
    def check_break_continue(instruction: list[Token], transpiler: 'Transpiler'):
        if instruction[0].type != Keyword.BREAK and instruction[0].type != Keyword.CONTINUE:
            return False

        if len(instruction) > 1:
            transpiler.data.newError(f"Unexpected token '{instruction[1].value}'", instruction[1].location)

        if transpiler.data.in_loop == 0:
            transpiler.data.newError(f"{instruction[0].type.code} statement must be in a loop", instruction[0].location)

        if instruction[0].type == Keyword.BREAK:
            transpiler.data.code_done.append("break;")
        else:
            transpiler.data.code_done.append("continue;")
        return True


    @staticmethod
    def do_for(line: list[Token], transpiler: 'Transpiler'):
        instruction = StringUtils.check_colon(line, transpiler)
        instruction_types = [token.type for token in instruction]

        if Keyword.IN not in instruction_types:
            transpiler.data.newError("For statement must contain 'in'", instruction[0].location)
            return

        left = instruction[1:instruction_types.index(Keyword.IN)]
        if not left:
            transpiler.data.newError("For statement must have a variable", instruction[0].location)
            return

        if len(left) > 1:
            transpiler.data.newError("For statement can only have one variable",
                                     Range.fromPositions(left[0].location.start, left[-1].location.end))
            return

        if left[0].type != Word.IDENTIFIER:
            transpiler.data.newError("Invalid Variable Name", left[0].location)
            return

        right = instruction[instruction_types.index(Keyword.IN) + 1:]
        if not right:
            transpiler.data.newError("For statement must have a iterable", instruction[0].location)
            return

        counter_name = left[0].value
        range_three = False

        if right[0].type == Word.IDENTIFIER and right[0].value == "range":
            if len(right) > 2:
                transpiler.data.newError("Can only have one range",
                                         Range.fromPositions(right[0].location.start, right[-1].location.end))
                return
            if len(right) < 2:
                transpiler.data.newError("Range must have Arguments",
                                         Range.fromPositions(right[0].location.start, right[-1].location.end))
                return

            if right[1].type != Brackets.ROUND:
                transpiler.data.newError("Range must have Arguments",
                                         Range.fromPositions(right[0].location.start, right[-1].location.end))
                return

            args = []
            last_comma = 0
            for i, token in enumerate(right[1].inside):
                if token.type == Separator.COMMA:
                    args.append(right[1].inside[last_comma:i])
                    last_comma = i + 1
            args.append(right[1].inside[last_comma:])

            if len(args) > 3:
                transpiler.data.newError("Range can only have 3 Arguments",
                                         Range.fromPositions(right[0].location.start, right[-1].location.end))
                args = args[:3]

            range_args = [Value.do_value(arg, transpiler) for arg in args]

            if len(range_args) == 1:
                transpiler.data.code_done.append(
                    f"for (int {counter_name} = 0; {counter_name} < {range_args[0].name}; {counter_name}++) {{")
            elif len(range_args) == 2:
                transpiler.data.code_done.append(
                    f"for (int {counter_name} = {range_args[0].name}; {counter_name} < {range_args[1].name}; {counter_name}++) {{")
            else:
                transpiler.data.code_done.append(f"if({range_args[0].name} < {range_args[1].name}) {{")
                transpiler.data.code_done.append(
                    f"for (int {counter_name} = {range_args[0].name}; {counter_name} < {range_args[1].name}; {counter_name} += {range_args[2].name}) {{")
                range_three = True
            counter = Variable(counter_name, PyduinoInt(), left[0].location)

        else:
            iterable = Value.do_value(right, transpiler)
            if not iterable.type.is_iterable():
                transpiler.data.newError("For statement must have a iterable", instruction[0].location)
                return

            transpiler.data.code_done.append(f"for (auto {left[0].value} : {iterable.name}) {{")
            counter = Variable(counter_name, iterable.type.item, left[0].location)

        end_line = StringUtils.get_indentation_range(transpiler.location.position.line + 1, transpiler)
        transpiler.scope.add_Variable(counter)

        transpiler.data.in_loop += 1
        len_before = len(transpiler.data.code_done)

        Control.check_indent(transpiler, "for")

        transpiler.data.in_loop -= 1
        transpiler.data.code_done.append("}")

        if range_three:
            transpiler.data.code_done.append("}\nelse {")
            transpiler.data.code_done.append(
                f"for (int {counter_name} = {range_args[0].name}; {counter_name} > {range_args[1].name}; {counter_name} += {range_args[2].name}) {{")
            transpiler.data.code_done.extend(transpiler.data.code_done[len_before:-2])
            transpiler.data.code_done.append("}")


if __name__ == '__main__':
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)


    t1 = time.time()
    print(fib(40))
    print("took ", time.time() - t1, " seconds")
