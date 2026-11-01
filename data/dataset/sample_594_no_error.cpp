#include <iostream>
class Handler {{
public:
    int add(int a, int b) {{ return a+b; }}
}};
int main() {{
    Handler obj;
    std::cout << obj.add(19,48);
    return 0;
}}