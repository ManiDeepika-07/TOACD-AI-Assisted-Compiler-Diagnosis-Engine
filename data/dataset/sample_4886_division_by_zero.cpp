#include <iostream>
int main() {
    int* ptr = new int(10);
    std::cout << *ptr << std::endl;
    delete ptr;
    int z = 10/0; return 0;
}