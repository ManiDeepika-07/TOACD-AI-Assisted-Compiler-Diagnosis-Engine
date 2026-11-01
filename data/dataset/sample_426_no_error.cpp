#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{79,77}};
    std::cout << p.x << " " << p.y;
    return 0;
}}