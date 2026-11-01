#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{29,78}};
    std::cout << p.x << " " << p.y;
    return 0;
}}