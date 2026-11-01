#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{16,88}};
    std::cout << p.x << " " << p.y;
    return 0;
}}