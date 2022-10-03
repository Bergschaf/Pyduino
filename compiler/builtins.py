def check_builtin(function_name, args, kwargs):
    if function_name == "print":
        return do_print(args, kwargs)

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
    return "cout << " + " << ' ' << ".join(args) + newline + ";"


