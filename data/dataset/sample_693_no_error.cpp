#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{67,75}};
    std::cout << p.x << " " << p.y;
    return 0;
}}