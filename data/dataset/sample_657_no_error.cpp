#include <iostream>
class Calculator {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Calculator obj;
    std::cout << obj.add(93,19);
    return 0;
}}