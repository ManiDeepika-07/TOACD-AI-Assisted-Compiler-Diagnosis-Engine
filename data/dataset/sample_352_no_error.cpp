#include <iostream>
int main() {
    int x = 34, y = 96;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}