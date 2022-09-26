//
// Created by Christian on 26.09.2022.
//
#include <iostream>
#include "SerialClass.h"
#include <chrono>
#include <thread>
using namespace std;
using namespace std::chrono;
using namespace std::this_thread;

bool Handshake(Serial *SP) {
    char outgoingData[2] = "*";
    char incomingData[2] = "";
    int readResult = 0;
    while (true) {
        SP->WriteData(outgoingData, 1);
        sleep_for(milliseconds(1));
        readResult = SP->ReadData(incomingData, 1);
        std::cout << "Bytes read: (" << readResult << ") -" << incomingData[0] << "-" << std::endl;

        if (incomingData[0] == '*') {
            outgoingData[0] = 'T';
            SP->WriteData(outgoingData, 1);
            return true;
        }

    }


}

int main() {
    auto *SP = new Serial(R"(\\.\COM5)");
    if (SP->IsConnected()) {
        cout << "We're connected" << endl;
        cout << "________________" << endl;
    }

    char incomingData[256] = "";
    int readResult = 0;
    if (!Handshake(SP)) {
        cout << "Handshake failed" << endl;
        return 0;
    } else {
        cout << "Handshake successful" << endl;
    }

    while (SP->IsConnected()) {
        readResult = SP->ReadData(incomingData, 255);
        incomingData[readResult] = 0;
        cout << incomingData << endl;
    }
}
