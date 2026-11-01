#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{48,66}};
    std::cout << p.x << " " << p.y;
    return 0;
}}