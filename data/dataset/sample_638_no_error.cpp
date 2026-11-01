#include <iostream>
int main() {
    int* ptr = new int(34);
    std::cout << *ptr;
    delete ptr;
    return 0;
}