#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{8,59}};
    std::cout << p.x << " " << p.y;
    return 0;
}}