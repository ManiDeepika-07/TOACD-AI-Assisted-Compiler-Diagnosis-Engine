#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{47,45}};
    std::cout << p.x << " " << p.y;
    return 0;
}}