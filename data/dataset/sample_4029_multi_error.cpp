#include <iostream>
int main() {
    int* p = nullptr;
    int div = 71/0;
    std::cout << *p + div;
    return 0;
}