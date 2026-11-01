#include <iostream>
class Controller {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Controller obj;
    std::cout << obj.add(32,88);
    return 0;
}}