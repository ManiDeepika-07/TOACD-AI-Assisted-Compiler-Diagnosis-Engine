#include <iostream>
int main() {
    int* p = nullptr;
    int div = 25/0;
    std::cout << *p + div;
    return 0;
}