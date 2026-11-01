#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{16,36}};
    std::cout << p.x << " " << p.y;
    return 0;
}}