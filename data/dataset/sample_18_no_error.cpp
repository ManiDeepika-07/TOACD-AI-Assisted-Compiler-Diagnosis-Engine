#include <iostream>
class Controller {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Controller obj;
    std::cout << obj.add(40,31);
    return 0;
}}