#include <iostream>
class Processor {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Processor obj;
    std::cout << obj.add(82,71);
    return 0;
}}