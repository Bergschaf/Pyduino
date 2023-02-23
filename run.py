import sys
import subprocess
from server.transpiler.runner import Runner

if __name__ == '__main__':
    #file = sys.argv[1]
    file = "test.pino"

    with open(file, "r") as f:
        runner = Runner(f.read())
        runner.run()
