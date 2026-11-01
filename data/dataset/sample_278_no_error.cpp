#include <iostream>
int main() {
    int* ptr = new int(42);
    std::cout << *ptr;
    delete ptr;
    return 0;
}