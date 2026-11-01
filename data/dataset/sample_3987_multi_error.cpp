#include <iostream>
int main() {
    int x;
    float f = 3.14f;
    int* p = &f;
    std::cout << x << *p;
    return 0;
}