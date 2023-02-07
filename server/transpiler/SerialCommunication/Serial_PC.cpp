# include "Serial.cpp"
# include <iostream>
# include <fstream>
# include <chrono>
# include <thread>

using namespace std;
using namespace std::chrono;
using namespace std::this_thread;

const char StartCharacter = '<';
const char EndCharacter = '>';
const char ResponseStartCharacter = '?';
const char ResponseEndCharacter = '!';

const int HandshakeTimeout = 10000;
const int DataTimeout = 500;
const int HandshakeResendTimeout = 10;
const int MessageCompleteTimeout = 10;

const int MaxRequests = 50;
const int MaxRequestsLength = 100;


template<typename T>
class Promise {
public:
    typedef T(bytesToType)(char *bytes);

    thread *t;

    static void
    resolve(int requestID, bytesToType bytesToType, T *targetVariable, char Responses[MaxRequests][MaxRequestsLength]) {
        int microsecondsWaited = 0;
        while (Responses[requestID][0] == 0) {
            sleep_for(microseconds(1));
            microsecondsWaited++;
            if (microsecondsWaited * 1000 > DataTimeout) {
                cout << "Error: Timeout while waiting for response" << endl;
                return;
            }
        }
        if (targetVariable == nullptr || bytesToType == nullptr) {
            Responses[requestID][0] = 0;
            return;
        }
        *targetVariable = bytesToType(Responses[requestID]);
        Responses[requestID][0] = 0;
    }

    Promise(T *targetVariable, bytesToType bytesToType, int requestID, char Responses[MaxRequests][MaxRequestsLength]) {
        // start a thread with the resolving function
        t = new thread(resolve, requestID, bytesToType, targetVariable, Responses);
    }

    // Destructor
    ~Promise() {
        // join the thread
        t->join();
    }
};


class Arduino {
    bool readData(char *data, int length) const {
        int bytesRead = 0;
        int start = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
        while (bytesRead < length) {
            int now = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
            if (now - start > MessageCompleteTimeout) {
                return false;
            }
            int bytes = SP->ReadData(data + bytesRead, length - bytesRead);
            bytesRead += bytes;

        }
        return true;
    }

    bool Handshake() {
        auto start = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();

        char random_x = rand() % 256;
        char outgoingData[3] = {StartCharacter, random_x, EndCharacter};
        char incomingData[3];

        SP->WriteData(outgoingData, 3);
        auto lastResend = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();


        while (true) {
            auto now = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
            if (now - start > HandshakeTimeout) {
                return false;
            }
            if (now - lastResend > HandshakeResendTimeout) {
                SP->WriteData(outgoingData, 3);
                lastResend = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
            }

            bool read = this->readData(incomingData, 3);
            if (read && incomingData[0] == StartCharacter && incomingData[2] == EndCharacter) {
                if (incomingData[1] == random_x) {
                    // read syn
                    this->readData(incomingData, 3);
                    if (incomingData[0] == StartCharacter && incomingData[2] == EndCharacter) {
                        // send syn
                        outgoingData[1] = incomingData[1];
                        SP->WriteData(outgoingData, 3);
                        return true;
                    }
                }
            }
        }
    }

    void decodeSerial(char *incomingData, int bytesRead, bool request) {
        if (request) {
            u_int requestID = incomingData[0];
            if (requestID >= MaxRequests) {
                cout << "Error: Request ID out of bounds" << endl;
                return;
            }

            u_int size = incomingData[1];
            if (size > MaxRequestsLength) {
                cout << "Error: Request size out of bounds" << endl;
                return;
            }

            char instruction = incomingData[2];
            char data[size];
            for (int i = 0; i < size; ++i) {
                data[i] = incomingData[i + 3];
            }
        } else {
            u_int requestID = incomingData[0];
            if (requestID >= MaxRequests) {
                cout << "Error: Request ID out of bounds" << endl;
                return;
            }

            u_int size = incomingData[1];
            if (size > MaxRequestsLength)
                cout << "Error: Request size out of bounds" << endl;

            for (int i = 0; i < size; ++i) {
                this->Responses[requestID][i + 1] = incomingData[i + 2];
            }
        }
    }


    void do_request(char instruction, char data[], int size) {
        if (instruction == 'l') {
            // print
            cout << "[Arduino:] ";
            for (int i = 0; i < size; ++i) {
                cout << data[i];
            }
            cout << endl;
        }
    }

    void send_request(char instruction, char data[], u_char size, u_char requestID) {
        char outgoingData[size + 5];
        outgoingData[0] = StartCharacter;
        outgoingData[1] = requestID;
        outgoingData[2] = size;
        outgoingData[3] = instruction;
        for (int i = 0; i < size; ++i) {
            outgoingData[i + 4] = data[i];
        }
        outgoingData[size + 4] = EndCharacter;
        SP->WriteData(outgoingData, size + 5);
    }

    void send_response(char data[], int size, int requestID) {
        char outgoingData[size + 4];
        outgoingData[0] = ResponseStartCharacter;
        outgoingData[1] = requestID;
        outgoingData[2] = size;
        for (int i = 0; i < size; ++i) {
            outgoingData[i + 3] = data[i];
        }
        outgoingData[size + 3] = ResponseEndCharacter;
        SP->WriteData(outgoingData, size + 4);
    }

    [[noreturn]]
    static void listener(Arduino *arduino, Serial *SP) {
        char incomingData[MaxRequestsLength];
        char dataBuffer[1];
        int readResult;
        while (true) {
            readResult = SP->ReadData(dataBuffer, 1);
            if (readResult == 0) {
                continue;
            }
            if (dataBuffer[0] != StartCharacter && dataBuffer[0] != ResponseStartCharacter) {
                continue;
            }
            int bytesRead = 0;
            bool request = dataBuffer[0] == StartCharacter;
            while (true) {
                readResult = SP->ReadData(dataBuffer, 1);
                if (readResult == 0) {
                    continue;
                }
                if (dataBuffer[0] == EndCharacter || dataBuffer[0] == ResponseEndCharacter) {
                    break;
                }
                incomingData[bytesRead] = dataBuffer[0];
                bytesRead++;
            }
            arduino->decodeSerial(incomingData, bytesRead, request);
        }
    }

    static short bytesToShort(char *bytes) {
        return (bytes[0] << 8) | bytes[1];
    }

    static int bytesToInt(char *bytes) {
        return (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
    }

    byte next_request_id() {
        if (request_id == MaxRequests) {
            request_id = 0;
        }
        request_id++;
        return request_id;
    }


public:
    char Responses[MaxRequests][MaxRequestsLength]{};
    byte request_id = 0;

    Serial *SP;
    thread *listenerThread;

    Arduino() {
        char portName[] = "COM5";
        SP = new Serial(portName);
        if (SP->IsConnected()) {
            cout << "Connected to " << portName << endl;
        } else {
            cout << "Error: Could not connect to " << portName << endl;
        }

        if (Handshake()) {
            cout << "Handshake successful" << endl;
        } else {
            cout << "Error: Handshake failed" << endl;
        }
        listenerThread = new thread(listener, this, SP);

    }

    int analogRead(int pin) {
        char data[1] = {static_cast<char>(pin)};
        byte id = next_request_id();
        send_request('a', data, 1, id);
        short result;
        delete new Promise<short>(&result, bytesToShort, 2, Responses);
        return result;
    }

    int digitalRead(int pin) {
        char data[1] = {static_cast<char>(pin)};
        byte id = next_request_id();
        send_request('c', data, 1, id);
        int result;
        delete new Promise<int>(&result, bytesToInt, 4, Responses);
        return result;
    }

    void analogWrite(int pin, int value) {
        char data[5] = {static_cast<char>(pin), static_cast<char>(value)};
        byte id = next_request_id();
        send_request('b', data, 2, id);
    }

};

