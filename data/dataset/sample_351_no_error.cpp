#include <iostream>
int main() {
    int* ptr = new int(77);
    std::cout << *ptr;
    delete ptr;
    return 0;
}