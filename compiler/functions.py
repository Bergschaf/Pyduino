from builtin_functions import check_builtin
from utils import *


def check_function_definition(line):
    pass


def check_function_execution(value):
    value = value.strip()
    if "(" not in value:
        return
    first_bracket = value.index("(")
    function_name = value[:first_bracket]

    print(value, first_bracket)

    second_bracket = find_closing_bracket_in_value(value, "(", first_bracket)
    arguments = value[first_bracket + 1:second_bracket]
    # TODO was wenn , in arguemtns?
    args, kwargs = do_arguments(arguments)

    if (f := check_builtin(function_name, args, kwargs)) is not None:
        return f
        # TODO check if function is defined

    """
    :return: (function translated to C++, return type, False here if the C++ representation works not as a function
    call with return type else True)
    """
    pass
