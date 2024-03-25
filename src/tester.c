#include <stdio.h>

int f1(int a[]){
    return 0;
}

int f2(int a[]){
    int b[2] = {2,3};
    return f1(a);
}

int main() {
    int a[2] = {3,4};
    f2(a);
}