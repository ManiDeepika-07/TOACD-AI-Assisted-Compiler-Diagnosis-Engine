#include <cstdlib>
#include <stdio.h>
int main() {
    int* p=(int*)malloc(sizeof(int));
    *p=42;
    free(p);
    char fmt[]="%n";
    printf(fmt);
    std::cout<<*p;
    return 0;
}