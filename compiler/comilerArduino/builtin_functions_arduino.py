from utils_arduino import next_sys_variable
import variables_arduino


def check_builtin(function_name, args, kwargs):
    if function_name == "print":
        print(args, kwargs)
        return do_print(args, kwargs)
    elif function_name == "analogRead":
        return do_analog_read(args, kwargs)
    elif function_name == "analogWrite":
        return do_analog_write(args, kwargs)
    elif function_name == "delay":
        return do_delay(args, kwargs)


def do_print(args, kwargs):
    newline = "<< endl"
    if "newline" in kwargs.keys():
        newline = "" if not kwargs["newline"] else "<< endl"
        if len(kwargs.keys()) > 1:
            raise Exception("print() got an unexpected keyword argument")
    else:
        if len(kwargs.keys()) > 0:
            raise Exception("print() got an unexpected keyword argument")
    return "cout << " + " << ' ' << ".join([a[0] for a in args]) + newline + ";", None, False


def do_analog_read(args, kwargs):
    variables_arduino.arduino_needed = True
    pin, dt = args[0]
    if dt != "int":
        raise Exception("analogRead() argument 1 must be 'int', not " + dt)
    if len(args) > 1:
        raise Exception("analogRead() takes exactly 1 argument")
    if len(kwargs.keys()) > 0:
        raise Exception("analogRead() got an unexpected keyword argument")
    sys_var = next_sys_variable()
    code = ["short " + sys_var + ";""arduino.analogRead(" + pin + ", &" + sys_var + ");"]
    [variables.code_done.append(l) for l in code]
    return sys_var, "int", True


def do_analog_write(args, kwargs):
    variables_arduino.arduino_needed = True
    pin, dt = args[0]
    value, dt2 = args[1]
    if dt != "int" or dt2 != "int":
        raise Exception("analogWrite() arguments  must be 'int', not " + dt)
    if len(args) > 2:
        raise Exception("analogWrite() takes exactly 2 arguments")
    if len(kwargs.keys()) > 0:
        raise Exception("analogWrite() got an unexpected keyword argument")
    return f"arduino.analogWrite(char({pin}), char({value}));", "void", True


def do_delay(args, kwargs):
    return f"sleep_for(milliseconds({args[0][0]}));", "void", True
