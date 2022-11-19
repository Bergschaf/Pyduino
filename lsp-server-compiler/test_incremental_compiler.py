from compiler import Compiler
import time
if __name__ == '__main__':
    file = "../testPyduino.pino"
    code = []
    while True:
        with open(file, "r") as f:
            new_code = f.readlines()

        if new_code != code:
            t1 = time.time()
            code = new_code
            compiler = Compiler(code,"pc")
            compiler.compile()
            print((time.time() - t1).__round__(4))
            print("\n".join([str(e) for e in compiler.errors]))
