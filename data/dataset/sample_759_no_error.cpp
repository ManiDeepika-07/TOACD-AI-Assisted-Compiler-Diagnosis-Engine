#include <iostream>
class Manager {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Manager obj;
    std::cout << obj.add(9,69);
    return 0;
}}