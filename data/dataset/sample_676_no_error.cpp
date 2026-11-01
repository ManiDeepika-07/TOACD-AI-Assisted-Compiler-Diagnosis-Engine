#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{37,93}};
    std::cout << p.x << " " << p.y;
    return 0;
}}