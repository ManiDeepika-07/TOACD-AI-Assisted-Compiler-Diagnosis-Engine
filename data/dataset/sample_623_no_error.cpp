#include <iostream>
int main() {
    int* ptr = new int(51);
    std::cout << *ptr;
    delete ptr;
    return 0;
}