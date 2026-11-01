#include <iostream>
int main() {
    int* ptr = new int(23);
    std::cout << *ptr;
    delete ptr;
    return 0;
}