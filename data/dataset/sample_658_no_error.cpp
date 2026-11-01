#include <iostream>
class Controller {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Controller obj;
    std::cout << obj.add(22,96);
    return 0;
}}