#include <iostream>
int main() {
    int x = 17, y = 12;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}