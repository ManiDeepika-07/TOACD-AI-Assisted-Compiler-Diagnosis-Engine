#include <iostream>
int main() {
    int* ptr = new int("string");
    std::cout << *ptr << std::endl;
    delete ptr;
    return 0;
}