#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{42,44}};
    std::cout << p.x << " " << p.y;
    return 0;
}}