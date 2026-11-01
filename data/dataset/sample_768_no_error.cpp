#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{36,21}};
    std::cout << p.x << " " << p.y;
    return 0;
}}