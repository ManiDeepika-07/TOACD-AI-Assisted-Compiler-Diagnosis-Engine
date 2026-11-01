#include <iostream>
int main() {
    int* p = nullptr;
    int div = 68/0;
    std::cout << *p + div;
    return 0;
}