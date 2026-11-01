#include <iostream>
class Processor {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Processor obj;
    std::cout << obj.add(46,49);
    return 0;
}}