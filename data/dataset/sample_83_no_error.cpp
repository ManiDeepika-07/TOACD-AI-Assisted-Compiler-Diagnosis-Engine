#include <iostream>
int main() {
    int* ptr = new int(73);
    std::cout << *ptr;
    delete ptr;
    return 0;
}