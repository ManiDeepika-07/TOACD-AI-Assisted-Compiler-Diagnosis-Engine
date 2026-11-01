#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{84,17}};
    std::cout << p.x << " " << p.y;
    return 0;
}}