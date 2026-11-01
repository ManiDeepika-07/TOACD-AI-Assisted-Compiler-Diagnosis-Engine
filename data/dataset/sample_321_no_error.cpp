#include <iostream>
int handle(int n) {{ if (n <= 1) return 1; return n * handle(n-1); }}
int main() {{
    std::cout << handle(69) << std::endl;
    return 0;
}}