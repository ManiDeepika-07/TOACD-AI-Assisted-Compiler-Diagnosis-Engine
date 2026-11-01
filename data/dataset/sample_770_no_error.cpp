#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{77,1}};
    std::cout << p.x << " " << p.y;
    return 0;
}}