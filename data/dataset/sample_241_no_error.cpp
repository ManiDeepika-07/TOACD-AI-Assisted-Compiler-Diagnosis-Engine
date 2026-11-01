#include <iostream>
int main() {
    int* ptr = new int(98);
    std::cout << *ptr;
    delete ptr;
    return 0;
}