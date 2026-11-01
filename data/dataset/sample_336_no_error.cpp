#include <iostream>
int main() {
    int* ptr = new int(25);
    std::cout << *ptr;
    delete ptr;
    return 0;
}