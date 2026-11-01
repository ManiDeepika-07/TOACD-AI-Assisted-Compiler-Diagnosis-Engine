#include <iostream>
int main() {
    int* p = nullptr;
    int div = 12/0;
    std::cout << *p + div;
    return 0;
}