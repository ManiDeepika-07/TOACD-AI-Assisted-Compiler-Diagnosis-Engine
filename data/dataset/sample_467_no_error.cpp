#include <iostream>
class Transformer {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Transformer obj;
    std::cout << obj.add(56,42);
    return 0;
}}