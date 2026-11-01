#include <iostream>
int main() {
    int x = 88, y = 44;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}