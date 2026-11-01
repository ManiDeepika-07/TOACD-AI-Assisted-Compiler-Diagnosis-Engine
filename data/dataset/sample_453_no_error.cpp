#include <iostream>
int main() {
    int* ptr = new int(22);
    std::cout << *ptr;
    delete ptr;
    return 0;
}