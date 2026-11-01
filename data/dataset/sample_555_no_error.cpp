#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{38,60}};
    std::cout << p.x << " " << p.y;
    return 0;
}}