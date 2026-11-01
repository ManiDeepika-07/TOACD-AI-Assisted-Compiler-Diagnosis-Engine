#include <iostream>
int main() {
    int* p = nullptr;
    int div = 45/0;
    std::cout << *p + div;
    return 0;
}