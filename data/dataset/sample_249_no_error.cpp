#include <iostream>
int main() {
    int* ptr = new int(89);
    std::cout << *ptr;
    delete ptr;
    return 0;
}