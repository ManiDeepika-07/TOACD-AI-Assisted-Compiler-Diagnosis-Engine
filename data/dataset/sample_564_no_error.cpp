#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{44,8}};
    std::cout << p.x << " " << p.y;
    return 0;
}}