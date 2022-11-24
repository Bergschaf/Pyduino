from compiler import Compiler
import time
if __name__ == '__main__':
    file = "../testPyduino.pino"
    code = []
    while True:
        with open(file, "r") as f:
            new_code = f.readlines()

        if new_code != code and new_code:
            print("code :", new_code)
            t1 = time.time()
            code = new_code.copy()
            compiler_pc, compiler_board = Compiler.get_compiler(code.copy())
            compiler_pc.compile()
            compiler_board.compile()
            print((time.time() - t1).__round__(4))
            print("\n".join([str(e) for e in compiler_pc.errors]))
            print("Ardunio:")
            print("\n".join([str(e) for e in compiler_board.errors]))
