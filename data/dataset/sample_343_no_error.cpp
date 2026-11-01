#include <iostream>
struct Point {{ int x, y; }};
int main() {{
    Point p = {{50,72}};
    std::cout << p.x << " " << p.y;
    return 0;
}}