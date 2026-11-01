#include <iostream>
int main() {
    int* ptr = new int(35);
    std::cout << *ptr;
    delete ptr;
    return 0;
}