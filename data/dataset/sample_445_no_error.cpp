#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{80,41}};
    std::cout << p.x << " " << p.y;
    return 0;
}}