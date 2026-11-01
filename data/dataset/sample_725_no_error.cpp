#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{4,76}};
    std::cout << p.x << " " << p.y;
    return 0;
}}