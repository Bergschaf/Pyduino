#include <iostream> //header file library 
using namespace std; //using standard library

int test(int a[]) {
    cout << "test" << a << endl;
    return 0;
}

int main() { //main function
    // output array
    int arr[] = {1, 2, 3, 4, 5};
    // size of array
    int n = sizeof(arr)/sizeof(arr[0]);
    // print array
    cout << "Array: ";
    cout << arr;
    test(new int[] {1,1,1});

    cout << "Hello World \n" << "h1" << 1; // first object
    cout << "Learn C++ \n\n"; //second object with blank line
    cout << "Educative Team"; //third object
    return 0; //no other output or return
} //end of code to exectute

