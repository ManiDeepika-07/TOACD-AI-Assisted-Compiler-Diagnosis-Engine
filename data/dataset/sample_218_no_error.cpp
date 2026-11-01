#include <iostream>
int main() {
    int x = 16, y = 82;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}