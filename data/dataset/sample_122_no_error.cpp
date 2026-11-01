#include <iostream>
int main() {
    int x = 43, y = 32;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}