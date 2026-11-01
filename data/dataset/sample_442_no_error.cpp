#include <iostream>
int main() {
    int* ptr = new int(67);
    std::cout << *ptr;
    delete ptr;
    return 0;
}