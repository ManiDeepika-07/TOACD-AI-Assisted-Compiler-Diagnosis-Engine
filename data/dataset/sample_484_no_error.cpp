#include <iostream>
int main() {
    int* ptr = new int(62);
    std::cout << *ptr;
    delete ptr;
    return 0;
}