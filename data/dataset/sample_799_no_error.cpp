#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{15,38}};
    std::cout << p.x << " " << p.y;
    return 0;
}}