#include <iostream>
int main() {
    int* ptr = new int(1);
    std::cout << *ptr;
    delete ptr;
    return 0;
}