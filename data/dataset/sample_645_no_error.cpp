#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{81,40}};
    std::cout << p.x << " " << p.y;
    return 0;
}}