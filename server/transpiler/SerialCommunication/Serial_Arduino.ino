using namespace std;

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

const byte analogPorts[6] = {A0, A1, A2, A3, A4, A5};

char Requests[MaxRequests];
char Responses[MaxRequests][MaxRequestsLength];

