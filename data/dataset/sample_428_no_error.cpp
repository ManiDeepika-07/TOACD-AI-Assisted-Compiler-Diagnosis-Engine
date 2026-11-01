#include <iostream>
int main() {
    int* ptr = new int(95);
    std::cout << *ptr;
    delete ptr;
    return 0;
}