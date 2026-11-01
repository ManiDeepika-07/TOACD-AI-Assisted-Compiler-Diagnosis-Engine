#include <iostream>
int main() {
    int* ptr = new int(92);
    std::cout << *ptr;
    delete ptr;
    return 0;
}