#include <iostream>
int main() {
    int* ptr = new int(63);
    std::cout << *ptr;
    delete ptr;
    return 0;
}