#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{56,95}};
    std::cout << p.x << " " << p.y;
    return 0;
}}