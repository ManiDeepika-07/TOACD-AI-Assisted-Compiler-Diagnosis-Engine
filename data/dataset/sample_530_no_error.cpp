#include <iostream>
int main() {
    int* ptr = new int(91);
    std::cout << *ptr;
    delete ptr;
    return 0;
}