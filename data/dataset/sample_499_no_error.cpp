#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{33,50}};
    std::cout << p.x << " " << p.y;
    return 0;
}}