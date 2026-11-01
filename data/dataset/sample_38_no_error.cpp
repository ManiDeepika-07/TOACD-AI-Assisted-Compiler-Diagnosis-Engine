#include <iostream>
int validate(int n) {{ if (n <= 1) return 1; return n * validate(n-1); }}
int main() {{
    std::cout << validate(7) << std::endl;
    return 0;
}}