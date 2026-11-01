#include <iostream>
class Calculator {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Calculator obj;
    std::cout << obj.add(74,4);
    return 0;
}}