#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{6,83}};
    std::cout << p.x << " " << p.y;
    return 0;
}}