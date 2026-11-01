#include <iostream>
int main() {
    int x = *(nullptr);
    int y = 20;
    int z = x + y;
    std::cout << z << std::endl;
    return 0;
}