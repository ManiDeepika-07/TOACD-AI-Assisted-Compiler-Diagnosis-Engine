#include <iostream>
int main() {
    int x = 67, y = 76;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}