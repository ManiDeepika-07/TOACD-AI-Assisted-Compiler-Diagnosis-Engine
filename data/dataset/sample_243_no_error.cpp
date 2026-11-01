#include <iostream>
int main() {
    int* ptr = new int(28);
    std::cout << *ptr;
    delete ptr;
    return 0;
}