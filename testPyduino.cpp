#include <iostream>
#include "SerialCommunication/SerialPc.cpp"
using namespace std;
int main() {
Arduino arduino = Arduino();
for (int i = 0; i < 255 ; i++) {
arduino.analogWrite(char(10), uint8_t (i));;
    sleep_for(milliseconds(50));;

}
}