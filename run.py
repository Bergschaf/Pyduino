import sys
import subprocess
from server.transpiler.runner import Runner

if __name__ == '__main__':
    if len(sys.argv) < 2:
        file = "test.pino"
    else:
        file = sys.argv[1]

    with open(file, "r") as f:
        runner = Runner(f.read())
        runner.run()
