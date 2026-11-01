#include <iostream>
int main() {
    int* ptr = new int(57);
    std::cout << *ptr;
    delete ptr;
    return 0;
}