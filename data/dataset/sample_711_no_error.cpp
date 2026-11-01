#include <iostream>
int calculate(int n) {{ if (n <= 1) return 1; return n * calculate(n-1); }}
int main() {{
    std::cout << calculate(11) << std::endl;
    return 0;
}}