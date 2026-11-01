#include <iostream>
int execute(int n) {{ if (n <= 1) return 1; return n * execute(n-1); }}
int main() {{
    std::cout << execute(91) << std::endl;
    return 0;
}}