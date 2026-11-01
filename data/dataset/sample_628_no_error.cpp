#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{85,64}};
    std::cout << p.x << " " << p.y;
    return 0;
}}