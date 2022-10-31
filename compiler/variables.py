
class Variables:
    def __init__(self):
        self.connection_needed = False
        self.code_done = []
        self.currentLineIndex = 0
        self.iterator = None
        self.SysVariableIndex = 0
        self.iteratorLineIndex = 0
        self.builtins_needed = []
        self.indentations = []
