#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{27,96}};
    std::cout << p.x << " " << p.y;
    return 0;
}}