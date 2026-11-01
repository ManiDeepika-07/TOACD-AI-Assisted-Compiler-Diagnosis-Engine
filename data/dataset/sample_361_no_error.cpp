#include <iostream>
int main() {
    int* ptr = new int(16);
    std::cout << *ptr;
    delete ptr;
    return 0;
}