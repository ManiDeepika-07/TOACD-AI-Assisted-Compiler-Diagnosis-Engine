#include <iostream>
int main() {
    int x = 77, y = 10;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}