#include <iostream>
int main() {
    int x = 83, y = 25;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}