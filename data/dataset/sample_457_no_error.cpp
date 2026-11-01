#include <iostream>
int main() {
    int x = 98, y = 11;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}