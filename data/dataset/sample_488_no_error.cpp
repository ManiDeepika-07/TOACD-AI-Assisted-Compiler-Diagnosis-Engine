#include <iostream>
int main() {
    int* ptr = new int(72);
    std::cout << *ptr;
    delete ptr;
    return 0;
}