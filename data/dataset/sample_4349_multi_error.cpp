#include <iostream>
int main() {
    int* p = nullptr;
    int div = 44/0;
    std::cout << *p + div;
    return 0;
}