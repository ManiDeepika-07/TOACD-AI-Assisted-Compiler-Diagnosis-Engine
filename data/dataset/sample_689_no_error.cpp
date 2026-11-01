#include <iostream>
int main() {
    int x = 84, y = 52;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}