#include <iostream>
int evaluate(int n) {{ if (n <= 1) return 1; return n * evaluate(n-1); }}
int main() {{
    std::cout << evaluate(39) << std::endl;
    return 0;
}}