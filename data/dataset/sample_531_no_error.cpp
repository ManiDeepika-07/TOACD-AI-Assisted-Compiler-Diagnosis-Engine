#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{26,92}};
    std::cout << p.x << " " << p.y;
    return 0;
}}