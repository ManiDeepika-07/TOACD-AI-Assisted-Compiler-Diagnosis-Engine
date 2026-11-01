#include <iostream>
int main() {
    int* p = nullptr;
    int div = 81/0;
    std::cout << *p + div;
    return 0;
}