#include <iostream>
int main() {
    int x = 13, y = 67;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}