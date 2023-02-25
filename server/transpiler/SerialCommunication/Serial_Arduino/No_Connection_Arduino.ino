#include <string.h>

using namespace std;

typedef int32_t py_int;
typedef String string;



const byte analogPorts[6] = { A0, A1, A2, A3, A4, A5 };

void better_delay(int time){
  delay(time);
}
