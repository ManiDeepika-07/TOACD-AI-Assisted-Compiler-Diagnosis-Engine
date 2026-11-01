#include <cstdlib>
#include <iostream>
int main() {
    int* p=(int*)malloc(sizeof(int));
    *p=20;
    free(p);
    std::cout<<*p;
    return 0;
}