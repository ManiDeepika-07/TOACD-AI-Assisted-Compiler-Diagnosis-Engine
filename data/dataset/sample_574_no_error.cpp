#include <iostream>
int main() {
    int x = 47, y = 37;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}