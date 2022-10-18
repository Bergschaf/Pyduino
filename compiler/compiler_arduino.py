from intitializer_arduino import intialize
from utils_arduino import do_line
import variables_arduino
from constants_arduino import SERIAL_CODE


def compile_arduino(code):
    intialize(code)
    for variables_arduino.currentLineIndex, line in variables_arduino.iterator:
        variables_arduino.code_done.append(do_line(line))
    variables_arduino.code_done.append("}")
    variables_arduino.code_done.insert(1, "innit_serial();")
    # insert "checkSerial();" after every line
    for i in range(1,len(variables_arduino.code_done)-1):
        if variables_arduino.code_done[i] == "}":
            continue
        variables_arduino.code_done.insert(i + i, "checkSerial();")

    variables_arduino.code_done.append("void loop() {checkSerial();}")
    return "\n".join([SERIAL_CODE] + variables_arduino.code_done)