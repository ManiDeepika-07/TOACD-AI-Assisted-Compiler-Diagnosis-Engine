#include <iostream>
int compute(int n) {{ if (n <= 1) return 1; return n * compute(n-1); }}
int main() {{
    std::cout << compute(41) << std::endl;
    return 0;
}}