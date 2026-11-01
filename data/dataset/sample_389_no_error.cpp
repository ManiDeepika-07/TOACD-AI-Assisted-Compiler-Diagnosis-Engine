#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{15,98}};
    std::cout << p.x << " " << p.y;
    return 0;
}}