import variables_arduino
from utils_arduino import get_line_identation


def intialize(code):
    """
    :param code: the code as list of lines
    """
    variables_arduino.totalLineCount = len(code)
    for line in code:
        variables_arduino.identations.append(get_line_identation(line))
    variables_arduino.code = code.copy()
    variables_arduino.code_done = ["void setup() {"]
    current_id_level = 0
    variables_arduino.scope = {(0, variables_arduino.totalLineCount): [[], []]}
    tempidscope = {
        (0, variables_arduino.totalLineCount): 0}  # keeps track of the id levels fo the scopes, so they don't get duplicated
    for pos_i, i in enumerate(variables_arduino.identations):
        if i == current_id_level:
            continue
        for pos_j, j in enumerate(variables_arduino.identations[pos_i + 1:]):
            if j < i:
                for k in tempidscope.keys():
                    if k[0] <= pos_i <= k[1]:
                        if tempidscope[k] == i:
                            break
                else:
                    variables_arduino.scope[(pos_i, pos_j + pos_i)] = [[], []]
                    tempidscope[(pos_i, pos_j + pos_i)] = i
                break
        current_id_level = i
    variables_arduino.iterator = enumerate(variables_arduino.code)
