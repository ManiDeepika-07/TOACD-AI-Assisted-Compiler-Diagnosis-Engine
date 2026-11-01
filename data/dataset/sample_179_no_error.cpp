#include <iostream>
class Validator {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Validator obj;
    std::cout << obj.add(47,51);
    return 0;
}}