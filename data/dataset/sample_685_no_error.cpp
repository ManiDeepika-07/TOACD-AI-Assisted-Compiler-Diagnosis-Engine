#include <iostream>
int main() {
    int* ptr = new int(59);
    std::cout << *ptr;
    delete ptr;
    return 0;
}