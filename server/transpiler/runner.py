import subprocess

from server.transpiler.transpiler import Transpiler
import patoolib
import os
import sys

TEMP_FOLDER = "temp"
class Runner:
    def __init__(self, code: str):
        self.code = code
        self.runner_id = 0
        self.board: bool = False
        self.pc: bool = False
        self.compiled = False
        self.port = None


    def run(self):
        if not self.compiled:
            self.compile()
        #subprocess.call("cls", shell=True)
        PC_COMMAND = f'cmd /c "set PATH=%PATH%;{os.getcwd()}/mingw/MinGW/bin&temp_{self.runner_id}.exe"'
        BOARD_COMMAND = f"server\\transpiler\\arduino-cli.exe upload -p {self.get_port()} -b arduino:avr:uno {TEMP_FOLDER}/temp_board"

        if self.board:
            subprocess.run(BOARD_COMMAND, shell=True)
        if self.pc:
            subprocess.run(PC_COMMAND, shell=True)


    def compile(self):
        code_pc, code_board = Transpiler.get_code(self.code.splitlines())

        if not os.path.isdir(TEMP_FOLDER):
            os.mkdir(TEMP_FOLDER)

        if not os.path.isdir(f"{TEMP_FOLDER}/temp_board"):
            os.mkdir(f"{TEMP_FOLDER}/temp_board")

        if code_pc:
            with open(f"{TEMP_FOLDER}/temp_pc.cpp", "w") as f:
                f.write(code_pc)

        if code_board:
            with open(f"{TEMP_FOLDER}/temp_board/temp_board.ino", "w") as f:
                f.write(code_board)


        # TODO use multiprocessing, compile_oc and compile_board in parallel
        PC_COMMAND =f'cmd /c "set PATH=%PATH%;{os.getcwd()}/mingw/MinGW/bin&g++ {TEMP_FOLDER}/temp_pc.cpp -o temp_{self.runner_id}.exe'
        BOARD_COMMAND = f"server\\transpiler\\arduino-cli.exe compile -b arduino:avr:uno {TEMP_FOLDER}/temp_board"

        if code_board and code_pc:
            p1 = subprocess.Popen(PC_COMMAND, shell=True)
            self.check_mingw()
            p2 = subprocess.Popen(BOARD_COMMAND, shell=True)
            p1.wait()
            p2.wait()
            self.pc = True
            self.board = True

        elif code_pc:
            self.check_mingw()
            subprocess.run(PC_COMMAND, shell=True)
            self.pc = True

        elif code_board:
            subprocess.run(BOARD_COMMAND, shell=True)
            self.board = True

        self.compiled = True

    def get_port(self):
        if os.path.isfile("temp/port.txt"):
            with open("temp/port.txt", "r") as f:
                self.port = f.read()
            return self.port

        if self.port:
            return self.port

        boards = [p.split(" ") for p in
                  subprocess.run(["server/transpiler/arduino-cli", "board", "list"], capture_output=True).stdout.decode(
                      "utf-8").split("\n")[1:] if "arduino" in p]
        if len(boards) == 0:
            print("No boards found, connect a board and try again")
            exit()
        print("Boards found:")
        for i, b in enumerate(boards):
            print(f"{i + 1}. {b[0]} - {b[-2]}")
        with open("temp/port.txt", "w") as f:
            f.write(boards[0][0])
        self.port = boards[0][0]
        return boards[0][0]

    def check_mingw(self):
        if not os.path.exists("mingw/MinGW/bin/g++.exe"):
            print("Extracting MinGW...")
            patoolib.extract_archive("mingw/MinGW.7z", outdir="mingw")
            print("MinGW installed")



