#include <iostream>
void doNothing() {}
int main() {
    int x = doNothing();
    std::cout << x << std::endl;
    return 0;
}