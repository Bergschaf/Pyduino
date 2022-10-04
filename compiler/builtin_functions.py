from utils import next_sys_variable
import variables


def check_builtin(function_name, args, kwargs):
    if function_name == "print":
        print(args,kwargs)
        return do_print(args, kwargs)
    elif function_name == "analogRead":
        return do_analog_read(args, kwargs)
    return False


def do_print(args, kwargs):
    newline = "<< endl"
    if "newline" in kwargs.keys():
        newline = "" if not kwargs["newline"] else "<< endl"
        if len(kwargs.keys()) > 1:
            raise Exception("print() got an unexpected keyword argument")
    else:
        if len(kwargs.keys()) > 0:
            raise Exception("print() got an unexpected keyword argument")
    return "cout << " + " << ' ' << ".join([a[0] for a in args]) + newline + ";"


def do_analog_read(args, kwargs):
    pin, dt = args[0]
    print("args: ",args)
    if dt != "int":
        raise Exception("analogRead() argument 1 must be 'int', not " + dt)
    if len(args) > 1:
        raise Exception("analogRead() takes exactly 1 argument")
    if len(kwargs.keys()) > 0:
        raise Exception("analogRead() got an unexpected keyword argument")
    sys_var = next_sys_variable()
    sys_var2 = next_sys_variable()
    code = ["int *" + sys_var + ";", "int " + sys_var2 + ";", "arduino.analogRead(" + pin + ", " + sys_var + ");",
            sys_var2 + " = *" + sys_var + ";"]
    [variables.code_done.append(l) for l in code]
    return sys_var2 , "int", True
