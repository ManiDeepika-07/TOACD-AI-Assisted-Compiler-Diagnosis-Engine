#include <iostream>
int main() {
    int* ptr = new int(56);
    std::cout << *ptr;
    delete ptr;
    return 0;
}