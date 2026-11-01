#include <iostream>
class Calculator {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Calculator obj;
    std::cout << obj.add(28,20);
    return 0;
}}