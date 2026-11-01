#include <iostream>
int main() {
    int* ptr = new int(40);
    std::cout << *ptr;
    delete ptr;
    return 0;
}