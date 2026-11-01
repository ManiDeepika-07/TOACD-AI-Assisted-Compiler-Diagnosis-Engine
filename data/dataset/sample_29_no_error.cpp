#include <iostream>
int main() {
    int x = 49, y = 1;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}