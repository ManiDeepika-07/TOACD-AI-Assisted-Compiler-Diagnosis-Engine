#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{83,32}};
    std::cout << p.x << " " << p.y;
    return 0;
}}