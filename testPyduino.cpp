#include <iostream>
            using namespace std;
int main(){
int x[] = {2, 4, 2, 4, 3, 2};
for (int i = 0; i <  sizeof(x) / sizeof(x[0])  ; i++) {
for (int j = i; j <  sizeof(x) / sizeof(x[0])  ; j++) {
if (x<x[min]) {
int min = i;
min = j;
}
int temp = x[min];
}
x[min] = x[i];
x[i] = temp;
for (int i = 0; i < sizeof(x) / sizeof(x[0]); i++) cout << x[i] << ' ';;
}
}