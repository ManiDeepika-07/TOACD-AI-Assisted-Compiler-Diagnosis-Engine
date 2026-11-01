#include <iostream>
int main() {
    int* ptr = new int(6);
    std::cout << *ptr;
    delete ptr;
    return 0;
}