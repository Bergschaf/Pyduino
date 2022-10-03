import variables
from constants import *
from utils import get_line_identation


def intialize(code):
    """
    :param code: the code as list of lines
    """
    variables.totalLineCount = len(code)
    for line in code:
        variables.identations.append(get_line_identation(line))
    variables.code = code.copy()
    current_id_level = 0
    variables.scope = {(0, variables.totalLineCount): [[], []]}
    tempidscope = {
        (0, variables.totalLineCount): 0}  # keeps track of the id levels fo the scopes, so they don't get duplicated
    for pos_i, i in enumerate(variables.identations):
        if i == current_id_level:
            continue
        for pos_j, j in enumerate(variables.identations[pos_i + 1:]):
            if j < i:
                for k in tempidscope.keys():
                    if k[0] <= pos_i <= k[1]:
                        if tempidscope[k] == i:
                            break
                else:
                    variables.scope[(pos_i, pos_j + pos_i)] = [[], []]
                    tempidscope[(pos_i, pos_j + pos_i)] = i
                break
        current_id_level = i
    variables.iterator = enumerate(variables.code)

