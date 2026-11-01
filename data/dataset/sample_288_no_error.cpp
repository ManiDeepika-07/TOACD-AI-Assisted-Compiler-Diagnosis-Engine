#include <iostream>
int main() {
    int* ptr = new int(18);
    std::cout << *ptr;
    delete ptr;
    return 0;
}