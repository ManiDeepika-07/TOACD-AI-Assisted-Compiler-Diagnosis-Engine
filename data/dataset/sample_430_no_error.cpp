#include <iostream>
int main() {
    int* ptr = new int(75);
    std::cout << *ptr;
    delete ptr;
    return 0;
}