#include <iostream>
int main() {
    int* ptr = new int(undeclared_var);
    std::cout << *ptr << std::endl;
    delete ptr;
    return 0;
}