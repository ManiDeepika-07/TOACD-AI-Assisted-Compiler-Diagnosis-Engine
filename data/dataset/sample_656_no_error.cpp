#include <iostream>
int main() {
    int x = 64, y = 6;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}