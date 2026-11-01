#include <iostream>
int main() {
    int* ptr = new int(84);
    std::cout << *ptr;
    delete ptr;
    return 0;
}