#include <iostream>
class Calculator {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Calculator obj;
    std::cout << obj.add(19,17);
    return 0;
}}