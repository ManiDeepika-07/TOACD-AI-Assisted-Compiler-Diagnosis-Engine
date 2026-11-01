#include <iostream>
int main() {
    int* ptr = new int(58);
    std::cout << *ptr;
    delete ptr;
    return 0;
}