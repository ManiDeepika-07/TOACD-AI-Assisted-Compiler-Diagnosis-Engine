#include <iostream>
int main() {
    int* ptr = new int(11);
    std::cout << *ptr;
    delete ptr;
    return 0;
}