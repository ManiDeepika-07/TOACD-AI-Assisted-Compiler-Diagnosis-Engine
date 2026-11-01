#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{23,79}};
    std::cout << p.x << " " << p.y;
    return 0;
}}