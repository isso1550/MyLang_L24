#include <stdio.h>
#include <stdbool.h>

struct myType {
    int a;
    int b;
};

int add_ints_struct(struct myType a){
    return a.a + a.b;
}

int main() {
    struct myType a;
    a.a = 1;
    a.b = 2;
    int c = add_ints_struct(a);
    printf("%d", c);
}