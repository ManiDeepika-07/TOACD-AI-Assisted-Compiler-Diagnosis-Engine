#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{90,61}};
    std::cout << p.x << " " << p.y;
    return 0;
}}