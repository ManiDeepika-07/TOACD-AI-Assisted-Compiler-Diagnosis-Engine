#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{14,84}};
    std::cout << p.x << " " << p.y;
    return 0;
}}