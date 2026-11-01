#include <iostream>
int main() {
    int x = 37, y = 31;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}