#include <iostream>
int main() {
    int x = 32, y = 19;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}