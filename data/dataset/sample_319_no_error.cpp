#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{70,63}};
    std::cout << p.x << " " << p.y;
    return 0;
}}