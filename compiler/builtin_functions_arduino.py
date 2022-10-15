from utils_arduino import next_sys_variable
import variables_arduino


def check_builtin(function_name, args, kwargs):
    if function_name == "print":
        return do_print(args, kwargs)
    elif function_name == "analogRead":
        return do_analog_read(args, kwargs)
    elif function_name == "analogWrite":
        return do_analog_write(args, kwargs)
    elif function_name == "delay":
        return do_delay(args, kwargs)


def do_print(args, kwargs):
    variables_arduino.arduino_needed = True
    newline = "true"
    if "newline" in kwargs.keys():
        newline = "false" if not kwargs["newline"] else "true"
        if len(kwargs.keys()) > 1:
            raise Exception("print() got an unexpected keyword argument")
    else:
        if len(kwargs.keys()) > 0:
            raise Exception("print() got an unexpected keyword argument")
    var = next_sys_variable()
    variables_arduino.code_done.append(f"String {var}[] = {{ {', '.join([f'String({arg[0]})' for arg in args])} }};")
    return f"do_print({var}, {len(args)}, {newline})", None, False


def do_analog_read(args, kwargs):
    variables_arduino.arduino_needed = True
    pin, dt = args[0]
    if dt != "int":
        raise Exception("analogRead() argument 1 must be 'int', not " + dt)
    if len(args) > 1:
        raise Exception("analogRead() takes exactly 1 argument")
    if len(kwargs.keys()) > 0:
        raise Exception("analogRead() got an unexpected keyword argument")
    return f"analogRead(A{pin})", "int", True


def do_analog_write(args, kwargs):
    variables_arduino.arduino_needed = True
    pin, dt = args[0]
    value, dt2 = args[1]
    if dt != "int" and dt is not None:
        raise Exception("analogWrite() arguments  must be 'int', not " + dt)
    if dt2 != "int" and dt2 is not None:
        raise Exception("analogWrite() arguments  must be 'int', not " + dt2)
    if len(args) > 2:
        raise Exception("analogWrite() takes exactly 2 arguments")
    if len(kwargs.keys()) > 0:
        raise Exception("analogWrite() got an unexpected keyword argument")
    return f"analogWrite({pin}, {value});", "void", True


def do_delay(args, kwargs):
    if args[0][1] != "int":
        raise Exception("delay() argument 1 must be 'int', not " + args[0][1])
    return f"delay({args[0][0]})", "void", True
