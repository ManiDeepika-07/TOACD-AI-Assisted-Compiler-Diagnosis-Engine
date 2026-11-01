#include <iostream>
int main() {
    int* ptr = new int(87);
    std::cout << *ptr;
    delete ptr;
    return 0;
}