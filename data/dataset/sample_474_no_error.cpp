#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{17,23}};
    std::cout << p.x << " " << p.y;
    return 0;
}}