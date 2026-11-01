#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{36,27}};
    std::cout << p.x << " " << p.y;
    return 0;
}}