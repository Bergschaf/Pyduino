filenames = ["control.py", "function.py", "pyduino_utils.py", "runner.py", "transpiler.py", "scope.py",
             "tokenizer.py", "variable.py", "../server.py", "SerialCommunication/Serial_PC.cpp",
                 "SerialCommunication/Serial_Arduino/Serial_Arduino.ino"]
# count lines of code
total = 0
d = "Server/transpiler/"
for filename in filenames:
    with open(d + filename, "r") as f:
        total += len(f.readlines())
print(f"Total lines of code: {total}")

# count words
total = 0
for filename in filenames:
    with open(d + filename, "r") as f:
        total += len(f.read().split())
print(f"Total words of code: {total}")

# count characters
total = 0
for filename in filenames:
    with open(d + filename, "r") as f:
        total += len(f.read())
print(f"Total characters of code: {total}")
