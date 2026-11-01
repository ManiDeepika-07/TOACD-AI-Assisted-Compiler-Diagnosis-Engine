#include <iostream>
int main() {
    int x = 82, y = 42;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}