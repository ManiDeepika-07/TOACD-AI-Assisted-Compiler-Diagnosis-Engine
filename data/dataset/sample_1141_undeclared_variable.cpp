#include <iostream>
int main() {
    int x = undeclared_var;
    int y = 20;
    int z = x + y;
    std::cout << z << std::endl;
    return 0;
}