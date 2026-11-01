#include <iostream>
int main() {
    int* ptr = new int(68);
    std::cout << *ptr;
    delete ptr;
    return 0;
}