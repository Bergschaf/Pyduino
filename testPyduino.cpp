#include <iostream>
            using namespace std;
int main(){
int x[] = {4, 1, 6, 2, 98, 3, 7, 8, 9, 10};
for (int i = 0; i < sizeof(x) / sizeof(x[0]); i++) cout << x[i] << ' ';cout << endl;;
for (int i = 0; i <  sizeof(x) / sizeof(x[0])  ; i++) {
int min = i;
for (int j = i; j <  sizeof(x) / sizeof(x[0])  ; j++) {
if (x[j]<x[min]) {
min = j;
}
}

int temp = x[min];
x[min] = x[i];
x[i] = temp;
}

for (int i = 0; i < sizeof(x) / sizeof(x[0]); i++) cout << x[i] << ' ';cout << endl;;
}