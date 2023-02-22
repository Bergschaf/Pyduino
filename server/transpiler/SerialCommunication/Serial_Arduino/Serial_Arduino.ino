#include <string.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

using namespace std;
LiquidCrystal_I2C lcd(0x27, 16, 2);

typedef int32_t py_int;
typedef String string;

const char StartCharacter = '<';
const char EndCharacter = '>';
const char ResponseStartCharacter = '?';
const char ResponseEndCharacter = '!';

const int HandshakeTimeout = 10000;
const int DataTimeout = 500;
const int HandshakeResendTimeout = 10;
const int MessageCompleteTimeout = 10;

const int MaxRequests = 5;
const int MaxRequestsLength = 100;

const byte analogPorts[6] = { A0, A1, A2, A3, A4, A5 };

int requestID = 0;
char Responses[MaxRequests][MaxRequestsLength];
char Requests[MaxRequests];

bool Handshake() {
  long start = millis();
  while (millis() - start < HandshakeTimeout) {
    if (Serial.available() >= 3) {
      uint8_t buffer[3];
      Serial.readBytes(buffer, 3);

      if (buffer[0] == StartCharacter && buffer[2] == EndCharacter) {
        Serial.write(buffer, 3);
        uint8_t r = random(255);
        buffer[1] = r;
        Serial.write(buffer, 3);
        while (Serial.available() < 3) {
        }
        Serial.readBytes(buffer, 3);
        if (buffer[1] == r) {
          return true;
        } else {
          return false;
        }
      }
    }
  }
  return false;
}




char getNextRequestId() {
  if (requestID >= MaxRequests) {
    requestID = 0;
  }
  requestID++;
  return requestID;
}


// TODO implement asynchronous waiting for data
void sendRequest(char instruction, const char *value, int valueSize, char requestId = 0) {
  char outgoingData[5 + valueSize];
  outgoingData[0] = StartCharacter;
  if (requestId == 0) {
    requestId = getNextRequestId();
  }
  outgoingData[1] = requestId;
  Requests[requestId] = instruction;

  outgoingData[2] = (char)valueSize;

  outgoingData[3] = instruction;

  for (int i = 0; i < valueSize; i++) {
    outgoingData[4 + i] = value[i];
  }

  outgoingData[4 + valueSize] = EndCharacter;

  Serial.write(outgoingData, 5 + valueSize);
}

void sendResponse(char requestID, const char *response, int responseSize) {
  char outgoingData[4 + responseSize];
  outgoingData[0] = StartCharacter;

  outgoingData[1] = requestID;

  outgoingData[2] = (char)responseSize;

  for (int i = 0; i < responseSize; i++) {
    outgoingData[3 + i] = response[i];
  }

  outgoingData[3 + responseSize] = EndCharacter;

  Serial.write(outgoingData, 4 + responseSize);
}

void decodeResponse(const char *data, int size) {
  char requestID = data[1];
  int responseSize = uint8_t (data[2]);
  Responses[requestID][0] = 1;

  for (int i = 0; i < responseSize; i++) {
    Responses[requestID][i + 1] = data[3 + i];
  }
}

void decodeRequest(const byte *data, int size) {
  char requestID = data[1];
  char instruction = data[3];
  int valueSize = int(uint8_t(data[2]));

  if (valueSize > MaxRequestsLength) {
    return;
    //cout << "Warning: value size is bigger than MaxDataLength" << endl;

  } else if (valueSize == 0) {
    Requests[requestID] = 0;

    //cout << "Warning: value size is 0" << endl;
    return;
  }
  char value[valueSize];
  for (int i = 0; i < valueSize; i++) {
    value[i] = data[4 + i];
  }
  if (instruction == 'a') {
    if (valueSize == 1) {
      short read = analogRead(analogPorts[value[0]]);
      const char response[2] = { (char)(read & 0xFF), (char)((read >> 8) & 0xFF) };
      sendResponse(requestID, response, 2);
    }
  } else if (instruction == 'b') {
    if (valueSize == 2) {
      analogWrite(value[0], int(uint8_t(value[1])));
      sendResponse(requestID, new char[1]{ ' ' }, 1);
    }
  }
}

void decodeSerial(const byte *data, int size, bool request) {
  if (request) {
    decodeRequest(data, size);
  } else  {
    decodeResponse(data, size);
  } 
}

void print(const String data, bool newline) {
  data += "\n";
  int len = data.length();
  char data_char[len];
  for (int i = 0; i < len; i++) {
    data_char[i] = data[i];
  }
  sendRequest('l', data_char, len);
}

void checkSerial() {
  if (Serial.available()) {
    char data = Serial.read();
    int incomingDataSize = 0;
    byte incomingData[MaxRequestsLength];
    if (data == StartCharacter || data == ResponseStartCharacter) {
      bool request = (data == StartCharacter);
      incomingDataSize = 1;
      incomingData[0] = data;
      while (incomingDataSize < MaxRequestsLength) {
        if (Serial.available()) {
          data = Serial.read();

          if (data == EndCharacter || data == ResponseEndCharacter) {
            incomingData[incomingDataSize] = data;
            decodeSerial(incomingData, incomingDataSize, request);
            incomingDataSize = 0;
            break;
          } else {
            incomingData[incomingDataSize] = data;
            incomingDataSize++;
          }
        }
      }
    }
  }
}

