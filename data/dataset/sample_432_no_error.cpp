#include <iostream>
void swap(int& a, int& b) {{ int t=a; a=b; b=t; }}
int main() {{
    int x=72, y=62;
    swap(x,y);
    std::cout << x << y;
    return 0;
}}