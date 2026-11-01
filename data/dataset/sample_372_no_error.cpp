#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{7,13}};
    std::cout << p.x << " " << p.y;
    return 0;
}}