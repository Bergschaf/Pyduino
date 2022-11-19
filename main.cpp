#include <iostream>
using namespace std;
void mergesort(int arr[],int res[], int l, int r, int size){
    if(l==r){
        res[l]=arr[l];
        return;
    }
    int mid = (l+r)/2;
    mergesort(arr,res,l,mid,size);
    mergesort(arr,res,mid+1,r,size);


}



int main() {
    while(true){
        ;
    }
}

