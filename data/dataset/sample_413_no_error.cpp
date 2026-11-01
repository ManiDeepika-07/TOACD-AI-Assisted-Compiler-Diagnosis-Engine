#include <iostream>
int process(int n) {{ if (n <= 1) return 1; return n * process(n-1); }}
int main() {{
    std::cout << process(65) << std::endl;
    return 0;
}}