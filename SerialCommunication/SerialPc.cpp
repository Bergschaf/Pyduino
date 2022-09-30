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

const int StartCharacter = 60; // <
const int EndCharacter = 62; // >
const int SpaceCharacter = 124; // |
const int MaxDataLength = 100;
const int MaxRequests = 50;
const int MaxMillisecondsToWaitForData = 2000;
char Requests[MaxRequests];
char Responses[MaxRequests][MaxDataLength];

bool Handshake(Serial *SP) {
    char outgoingData[2] = "*";
    char incomingData[2] = "";
    int readResult = 0;
    while (true) {
        SP->WriteData(outgoingData, 2);
        sleep_for(milliseconds(2));
        readResult = SP->ReadData(incomingData, 2);
        if (readResult > 0) {
            std::cout << "Bytes read: (" << readResult << ") -" << incomingData[0] << "-" << std::endl;

            if (incomingData[0] == '*') {
                outgoingData[0] = 'T';
                SP->WriteData(outgoingData, 1);
                readResult = SP->ReadData(incomingData, 1);
                while (readResult > 0) {
                    readResult = SP->ReadData(incomingData, 1);
                }
                return true;
            }
        }

    }
}

char getNextRequestId() {
    for (uint8_t i = 0; i < MaxRequests; i++) {
        if (Requests[i] == 0) {
            return (char) i;
        }
    }
    return -1;
}

// TODO implement asynchronous waiting for data
void sendRequest(char instruction, const char *value, int valueSize, Serial *SP) {
    char outgoingData[8 + valueSize];
    outgoingData[0] = StartCharacter;

    char requestId = getNextRequestId();
    outgoingData[1] = requestId;
    Requests[requestId] = instruction;

    outgoingData[2] = SpaceCharacter;

    outgoingData[3] = (char) valueSize;

    outgoingData[4] = SpaceCharacter;

    outgoingData[5] = instruction;

    outgoingData[6] = SpaceCharacter;

    for (int i = 0; i < valueSize; i++) {
        outgoingData[7 + i] = value[i];
    }

    outgoingData[7 + valueSize] = EndCharacter;
    /*cout << "Sending request: " << int(outgoingData[0]);
    for (int i = 1; i < 7 + valueSize; ++i) {
        cout << " " << int(outgoingData[i]) << " ";
    }
    cout << int(outgoingData[7 + valueSize]) << endl;*/
    SP->WriteData(outgoingData, 8 + valueSize);
}

void sendResponse(char requestID, const char *response, int responseSize, Serial *SP) {
    char outgoingData[6 + responseSize];
    outgoingData[0] = StartCharacter;

    outgoingData[1] = requestID;

    outgoingData[2] = SpaceCharacter;

    outgoingData[3] = (char) responseSize;

    outgoingData[4] = SpaceCharacter;

    for (int i = 0; i < responseSize; i++) {
        outgoingData[5 + i] = response[i];
    }

    outgoingData[6 + responseSize] = EndCharacter;

    SP->WriteData(outgoingData, 6 + responseSize);
}

void decodeResponse(const char *data, int size) {
    char requestID = data[1];
    char instruction = Requests[requestID];
    int responseSize = int(uint8_t(data[3]));

    if (responseSize > MaxDataLength) {
        cout << "Warning: response size is bigger than MaxDataLength" << endl;
        responseSize = MaxDataLength;
    } else if (responseSize == 0) {
        Requests[requestID] = 0;
        cout << "Warning: response size is 0" << endl;
        return;
    }
    if (data[2] != SpaceCharacter || data[4] != SpaceCharacter) {
        Requests[requestID] = 0;
        cout << "Error: Invalid response format" << endl;
        return;
    }
    for (int i = 0; i < responseSize; i++) {
        Responses[requestID][i] = data[5 + i];

    }
    char chars[2] = {Responses[requestID][0], Responses[requestID][1]};
    int v1 = int(uint8_t(chars[0])) ;
    int v2 = int(uint8_t(chars[1]));
    cout << "Response: " <<(v1 * 256) + v2 << endl;
    Requests[requestID] = 0;

    // convert the two chars at Responses[requestID] to one int

    Requests[requestID] = 0;
}

void decodeRequest(const char *data, int size) {

}

void decodeSerial(const char *data, int size) {
    char requestID = data[1];
    if (int(requestID) <= MaxRequests) {
        decodeResponse(data, size);
    } else if (int(requestID <= MaxRequests * 2)) {
        decodeRequest(data, size);
    } else {
        cout << "Error: Invalid Request ID";
    }

}


int main() {
    auto *SP = new Serial(R"(\\.\COM8)");
    if (SP->IsConnected()) {
        cout << "We're connected" << endl;
        cout << "________________" << endl;
    }

    char incomingData[1] = "";
    int readResult = 0;

    if (!Handshake(SP)) {
        cout << "Handshake failed" << endl;
        return 0;
    } else {
        cout << "Handshake successful" << endl;
    }

    sendRequest('a',new char[1] {0}, 1, SP);



    while (true) {
        readResult = SP->ReadData(incomingData, 1);
        if (readResult > 0) {
            if(incomingData[0] == StartCharacter){
                char data[MaxDataLength];
                data[0] = StartCharacter;
                int i = 1;

                while (true){
                    readResult = SP->ReadData(incomingData, 1);
                    if(readResult > 0){
                        data[i] = incomingData[0];
                        i++;
                        if(incomingData[0] == EndCharacter){
                            decodeSerial(data, i);
                            break;
                        }
                    }
                }
                sendRequest('a',new char[1] {0}, 1, SP);
                sleep_for(milliseconds(50));
            }
        }
    }

}
