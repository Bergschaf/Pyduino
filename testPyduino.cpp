#include "SerialCommunication/SerialPc.cpp"
#include <iostream>
using namespace std;
int main() {
Arduino arduino = Arduino();
cout << "Hello World"<< endl;;
while (true) {
short _sys_var_649974;arduino.analogRead(0, &_sys_var_649974);
int i =  _sys_var_649974 ;
cout << i<< endl;;
arduino.analogWrite(char(11), char(i / 4));;
sleep_for(milliseconds(50));;
}
sleep_for(milliseconds(1000000));;
}