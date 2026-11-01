#include <iostream>
int main() {
    float f = 3.14f;
    int* p = &f;
    std::cout << *p << std::endl;
    return 0;
}