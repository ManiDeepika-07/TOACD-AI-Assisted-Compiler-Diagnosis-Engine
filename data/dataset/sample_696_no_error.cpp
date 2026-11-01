#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{64,82}};
    std::cout << p.x << " " << p.y;
    return 0;
}}