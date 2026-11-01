#include <iostream>
int main() {
    int* ptr = new int(*(nullptr));
    std::cout << *ptr << std::endl;
    delete ptr;
    return 0;
}