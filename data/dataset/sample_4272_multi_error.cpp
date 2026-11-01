#include <iostream>
int main() {
    int* p = nullptr;
    int div = 14/0;
    std::cout << *p + div;
    return 0;
}