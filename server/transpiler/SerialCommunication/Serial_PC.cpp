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

const int HandshakeTimeout = 1000;
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
            sleep_for(microseconds (1));
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

    bool Handshake(){
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
            if(now - lastResend > HandshakeResendTimeout) {
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
                        SP->WriteData(outgoingData, 3);
                        return true;
                    }
                }
            }
        }

    }
public:
    char Requests[MaxRequests];
    char Responses[MaxRequests][MaxRequestsLength];

    Serial *SP;

};

