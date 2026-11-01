#include <cstdlib>
#include <iostream>
int main() {
    int* p=(int*)malloc(sizeof(int));
    *p=40;
    free(p);
    std::cout<<*p;
    return 0;
}