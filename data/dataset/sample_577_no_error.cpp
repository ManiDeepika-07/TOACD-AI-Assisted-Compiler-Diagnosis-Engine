#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{5,89}};
    std::cout << p.x << " " << p.y;
    return 0;
}}