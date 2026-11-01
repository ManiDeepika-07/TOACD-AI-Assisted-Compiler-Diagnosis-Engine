#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{12,28}};
    std::cout << p.x << " " << p.y;
    return 0;
}}