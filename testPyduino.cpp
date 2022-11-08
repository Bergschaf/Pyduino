#include <iostream>
            using namespace std;
            int main() {
int x[] = {2, 4, 2, 4, 3, 2};
for (int i = 0; i < sizeof(x) / sizeof(x[0]); i++) cout << x[i] << ' ';cout << 32<< ' ' <<"Hello" << endl;;
}