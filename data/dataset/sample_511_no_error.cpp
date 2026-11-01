#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{75,47}};
    std::cout << p.x << " " << p.y;
    return 0;
}}