from compiler import Compiler
from variables import Variables
from constants import Constants
import subprocess

code_pc = None
code_board = None
with open("../testPyduino.pino", "r") as f:
    code = [l.strip("\n").rstrip() for l in f.readlines() if l.strip("\n").replace(" ", "") != ""]
    if code[0] == "#main":
        for i in range(len(code)):
            if code[i] == "#board":
                code_pc = code[1:i]
                code_board = code[i + 1:]
                break
        else:
            code_pc = code[1:]
    elif code[0] == "#board":
        code_board = code[1:]
    else:
        raise SyntaxError("No start defined, it should be '#board' or '#main' at the beginning")

# main code
connection_needed = False
if code_pc is not None:
    compiler_pc = Compiler(Variables(), code_pc, "pc")
    c_code_pc = compiler_pc.compile()
    connection_needed = compiler_pc.Variables.connection_needed
    if code_board is not None:
        compiler_board = Compiler(Variables(), code_board, "arduino")
        c_code_board = compiler_board.compile()
        connection_needed = True if compiler_board.Variables.connection_needed else connection_needed
        c_code_board = compiler_board.finish(connection_needed)
        with open("../testPyduino/testPyduino.ino", "w") as f:
            f.write(c_code_board)
    c_code_pc = compiler_pc.finish(connection_needed)
    with open("../testPyduino.cpp", "w") as f:
        f.write(c_code_pc)


subprocess.run("arduino-cli compile --fqbn arduino:avr:uno ../testPyduino/testPyduino.ino", shell=True)
# list all device
out = subprocess.run("arduino-cli board list", shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8")
print("....................")
print(out.split("\n"))
# Upload to device on COM5
subprocess.run("arduino-cli upload -p COM8 --fqbn arduino:avr:uno ../testPyduino/testPyduino.ino", shell=True)
