#include <iostream>
using namespace std;
int main() {
int y=( 2 + 3 ) * 4;
float z=1.111;
char x='a';
bool b=y > z;
if (y > z) {
cout << "y is greater than z" << endl;
}
int count=0;
while (count < 10000) {
cout << count << endl;
count++;
}
cout << y << endl;
cout << z << endl;
cout << b << endl;
return 0;
}