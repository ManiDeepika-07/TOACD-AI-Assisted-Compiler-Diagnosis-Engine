#include <iostream>
int main() {
    int* ptr = new int(76);
    std::cout << *ptr;
    delete ptr;
    return 0;
}