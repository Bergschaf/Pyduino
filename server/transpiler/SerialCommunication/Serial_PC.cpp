# include <iostream>
# include "Serial.cpp"
# include <fstream>

using namespace std;


# include <chrono>
# include <thread>

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

const int MaxRequests = 5;
const int MaxRequestsLength = 50;


template<typename T>
class Promise {
public:
    typedef T(bytesToType)(char *bytes);

    thread *t;

    static void
    resolve(int requestID, bytesToType bytesToType, T *targetVariable, char Responses[MaxRequests][MaxRequestsLength]) {
        int microsecondsWaited = 0;
        //cout << "start waiting" << endl;
        while (Responses[requestID][0] == 0) {
            sleep_for(microseconds(1));
            microsecondsWaited++;
            if (microsecondsWaited / 1000 > DataTimeout) {
                cout << "Error: Timeout while waiting for response  request_id: " << requestID << endl;
                return;
            }
        }
        if (targetVariable == nullptr || bytesToType == nullptr) {
            Responses[requestID][0] = 0;
            return;
        }
        *targetVariable = bytesToType(Responses[requestID] + 1);
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
                //cout << "Error: Request ID out of bounds" << endl;
                //return;
            }

            u_int size = incomingData[1];
            if (size > MaxRequestsLength) {
                cout << "Error: Request size out of bounds" << endl;
                return;
            }

            char instruction = incomingData[2];
            char data[size];
            for (int i = 0; i < size; i++) {
                data[i] = incomingData[i + 3];
            }
            this->do_request(instruction, data, size, requestID);

        } else {
            u_int requestID = incomingData[0];
            if (requestID >= MaxRequests) {
                cout << "Error: Request ID out of bounds" << endl;
                return;
            }

            u_int size = incomingData[1];
            if (size > MaxRequestsLength) { cout << "Error: Request size out of bounds" << endl; }
            this->Responses[requestID][0] = 1;
            //cout << "hier" << endl;
            for (int i = 0; i < size; ++i) {
                this->Responses[requestID][i + 1] = incomingData[i + 2];
            }

        }
    }


    void do_request(char instruction, char data[], int size, int requestID) {
        if (instruction == 'l') {
            // print
            cout << "[Arduino:] ";
            for (int i = 0; i < size; ++i) {
                cout << data[i];
            }
        } else if (instruction == 'm') {
            char func_id = data[0];

            do_function(*this, data + 1, func_id, requestID);
        }
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

            //cout << "read: " << dataBuffer[0] << " | " << (int)static_cast<u_char>(dataBuffer[0]) << endl;
            if (dataBuffer[0] != StartCharacter && dataBuffer[0] != ResponseStartCharacter) {
                continue;
            }
            int bytesRead = 0;
            bool request = dataBuffer[0] == StartCharacter;
            while (true) {
                readResult = SP->ReadData(dataBuffer, 1);
                //cout << "read: " << dataBuffer[0] << " | "<< (int)static_cast<u_char>(dataBuffer[0]) << "  request: " << request<< endl;
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


public:
    char Responses[MaxRequests][MaxRequestsLength]{};
    char Requests[MaxRequests]{};
    char request_id = 0;

    Serial *SP;
    thread *listenerThread;

    void (*do_function)(Arduino, char *, char, char);

    Arduino() {
        // open "temp/port.txt" and read the port name
        ifstream portFile("temp/port.txt");
        string portNamef;
        portFile >> portNamef;
        portFile.close();
        const char* portName = portNamef.c_str();
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
        system("cls");
        listenerThread = new thread(listener, this, SP);

    }

    char next_request_id() {
        while (true) {
            for (int i = 0; i < MaxRequests; ++i) {
                if (Requests[i] == 0) {
                    Requests[i] = 1;
                    return i;
                }

            }
            cout << "Error: No free request id" << endl;
        }
    }

    static int bytesToInt(char *bytes) {
        return (*static_cast<int *>(static_cast<void *>(bytes)));
    }

    static short bytesToShort(char *bytes) {
        //cout << "bytesToShort: " << (int)static_cast<u_char>(bytes[0]) << " " << (int)static_cast<u_char>(bytes[1]) << endl;
        return (*static_cast<short *>(static_cast<void *>(bytes)));
    }

    static bool bytesToBool(char *bytes) {
        return (*static_cast<bool *>(static_cast<void *>(bytes)));
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

        //cout << "send response: ";
        //for (int i = 0; i < size+4; ++i) {
        //    cout << " ( " << outgoingData[i] << " | " << (int)(static_cast<u_char>(outgoingData[i])) << " ) ";
        //}
        //cout << endl;

        SP->WriteData(outgoingData, size + 4);
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


    int analogRead(int pin) {
        char data[2] = {0, static_cast<char>(pin)};
        char id = next_request_id();
        send_request('n', data, 2, id);
        short result;
        delete new Promise<short>(&result, bytesToShort, id, Responses);
        Requests[id] = 0;
        return result;
    }

    int digitalRead(int pin) {
        char data[2] = {2, static_cast<char>(pin)};
        char id = next_request_id();
        send_request('n', data, 1, id);
        bool result;
        delete new Promise<bool>(&result, bytesToBool, id, Responses);
        Requests[id] = 0;
        return (int) result;
    }

    void analogWrite(int pin, int value) {
        if (value > 255) {
            value = 255;
            cout << "Warning: analogWrite value to high, setting to 255" << endl;
        }
        char data[3] = {1, static_cast<char>(pin), static_cast<char>(value)};
        char id = next_request_id();
        send_request('n', data, 3, id);
        delete new Promise<int>(nullptr, nullptr, id, Responses);
        Requests[id] = 0;
    }

    void digitalWrite(int pin, int value) {
        if (value > 1) {
            value = 1;
            cout << "Warning: digitalWrite value to high, setting to 1" << endl;
        }
        if (value == 1) {
            value = 255;
        }
        analogWrite(pin, value);
    }

    void lcd_print(char *text) {
        cout << "lcd_print: " << text << " (not implemented)" << endl;
        char id = next_request_id();
        int size = strlen(text) + 1;
        char data[size];
        data[0] = 2;
        for (int i = 1; i < size; ++i) {
            data[i] = text[i-1];
        }
        send_request('o',data , strlen(text) + 1, id);
        delete new Promise<int>(nullptr, nullptr, id, Responses);
        Requests[id] = 0;
    }

    void lcd_setCursor(int x, int y) {
        cout << "lcd_setCursor: " << x << " " << y << " (not implemented)" << endl;
        char id = next_request_id();
        char data[3] = {1, static_cast<char>(x), static_cast<char>(y)};
        send_request('o', data, 3, id);
        delete new Promise<int>(nullptr, nullptr, id, Responses);
        Requests[id] = 0;
    }

    void lcd_clear() {
        cout << "lcd_clear: (not implemented)" << endl;
        char id = next_request_id();
        char data[1] = {3};
        send_request('o', data, 1, id);
        delete new Promise<int>(nullptr, nullptr, id, Responses);
        Requests[id] = 0;
    }

};

