#include <iostream>
int main() {
    int x = 48, y = 5;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}