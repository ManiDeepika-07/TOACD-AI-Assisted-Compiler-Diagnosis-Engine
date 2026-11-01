#include <iostream>
class Processor {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Processor obj;
    std::cout << obj.add(69,31);
    return 0;
}}