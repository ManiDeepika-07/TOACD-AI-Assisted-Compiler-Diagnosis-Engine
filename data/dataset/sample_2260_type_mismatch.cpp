#include <iostream>
struct Point { int x, y; };
int main() {
    Point p = {1, 2};
    int val = p;
    std::cout << val << std::endl;
    return 0;
}