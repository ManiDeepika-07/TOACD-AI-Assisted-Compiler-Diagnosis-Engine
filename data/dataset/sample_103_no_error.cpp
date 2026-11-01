#include <iostream>
int main() {
    int* ptr = new int(81);
    std::cout << *ptr;
    delete ptr;
    return 0;
}