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
        subprocess.call("cls", shell=True)
        if self.board:
            self.run_board()
        if self.pc:
            self.run_pc()

    def run_board(self):
        os.system(f"server\\transpiler\\arduino-cli.exe upload -p {self.get_port()} -b arduino:avr:uno {TEMP_FOLDER}/temp_board")

    def run_pc(self):
        os.system(f'cmd /c "set PATH=%PATH%;{os.getcwd()}/mingw/MinGW/bin&temp_{self.runner_id}.exe"')

    def compile(self):
        code_pc, code_board = Transpiler.get_code(self.code.splitlines())

        if code_pc:
            with open(f"{TEMP_FOLDER}/temp_pc.cpp", "w") as f:
                f.write(code_pc)

        if code_board:
            with open(f"{TEMP_FOLDER}/temp_board/temp_board.ino", "w") as f:
                f.write(code_board)

        # TODO use multiprocessing, compile_oc and compile_board in parallel
        if code_pc:
            self.compile_pc(f"{TEMP_FOLDER}/temp_pc.cpp")
            self.pc = True

        if code_board:
            self.compile_board(f"{TEMP_FOLDER}/temp_board")
            self.board = True
        self.compiled = True
    def compile_pc(self, path):
        self.check_mingw()
        os.system(
            f'cmd /c "set PATH=%PATH%;{os.getcwd()}/mingw/MinGW/bin&g++ {path} -o temp_{self.runner_id}.exe')

    def get_port(self):
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

    def compile_board(self, path):
        os.system(
            f'server\\transpiler\\arduino-cli.exe compile -b arduino:avr:uno {path}')

    def check_mingw(self):
        if not os.path.exists("mingw/MinGW/bin/g++.exe"):
            print("Extracting MinGW...")
            patoolib.extract_archive("mingw/MinGW.7z", outdir="mingw")
            print("MinGW installed")


