#include <iostream>
int main() {
    int* ptr = new int(33);
    std::cout << *ptr;
    delete ptr;
    return 0;
}