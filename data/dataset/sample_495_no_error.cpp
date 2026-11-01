#include <iostream>
int main() {
    int* ptr = new int(8);
    std::cout << *ptr;
    delete ptr;
    return 0;
}