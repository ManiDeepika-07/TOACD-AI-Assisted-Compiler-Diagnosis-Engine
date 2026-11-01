#include <iostream>
#include <cstdlib>
int main() {
    int* p = (int*)malloc(sizeof(int));
    *p = 42;
    free(p);
    std::cout << *p << std::endl;
    return 0;
}