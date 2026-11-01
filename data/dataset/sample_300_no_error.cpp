#include <iostream>
int transform(int n) {{ if (n <= 1) return 1; return n * transform(n-1); }}
int main() {{
    std::cout << transform(10) << std::endl;
    return 0;
}}