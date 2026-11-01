#include <iostream>
int main() {
    int* p = nullptr;
    int div = 28/0;
    std::cout << *p + div;
    return 0;
}