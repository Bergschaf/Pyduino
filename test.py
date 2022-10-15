import dis

def g(x):
    return x + 1

x = """def f():
    x = 10
    if g(x) == 11:
        return g(x)"""

code = compile(x, "test.py", "exec")

print(dis.disassemble(code))
