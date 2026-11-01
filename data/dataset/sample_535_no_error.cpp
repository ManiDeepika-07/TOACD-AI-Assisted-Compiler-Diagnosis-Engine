#include <iostream>
int main() {
    int x = 74, y = 17;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}