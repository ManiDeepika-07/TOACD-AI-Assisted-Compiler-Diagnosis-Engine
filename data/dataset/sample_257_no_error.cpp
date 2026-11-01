#include <iostream>
int main() {
    int x = 81, y = 64;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}