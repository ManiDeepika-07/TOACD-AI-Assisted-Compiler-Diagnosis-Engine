#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{21,10}};
    std::cout << p.x << " " << p.y;
    return 0;
}}