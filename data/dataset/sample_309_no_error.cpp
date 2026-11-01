#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{41,51}};
    std::cout << p.x << " " << p.y;
    return 0;
}}