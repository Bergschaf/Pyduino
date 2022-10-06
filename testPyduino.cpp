#include <iostream>
#include "SerialCommunication/SerialPc.cpp"
using namespace std;
int main() {
Arduino arduino = Arduino();
while (true) {
short _sys_var_649974;arduino.analogRead(0, &_sys_var_649974);
arduino.analogWrite(char(11), char(_sys_var_649974));;
}
}