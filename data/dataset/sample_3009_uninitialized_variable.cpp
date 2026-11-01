#include <iostream>
int main() {
    int* ptr = new int(var_uninit);
    std::cout << *ptr << std::endl;
    delete ptr;
    return 0;
}