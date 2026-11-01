#include <iostream>
int main() {
    int x = 84, y = 84;
    while (x > 0) {{ x -= y; }}
    std::cout << x;
    return 0;
}