#include <iostream>
int main() {
    int* ptr = new int(41);
    std::cout << *ptr;
    delete ptr;
    return 0;
}