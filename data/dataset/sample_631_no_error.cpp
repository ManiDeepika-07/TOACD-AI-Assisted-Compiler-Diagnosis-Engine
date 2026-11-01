#include <iostream>
int main() {
    int x = 21, y = 65;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}