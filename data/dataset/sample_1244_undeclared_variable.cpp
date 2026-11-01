#include <iostream>
void print_sum(int a, int b) {
    std::cout << (a + b) << std::endl;
}
int main() {
    int x = undeclared_var;
    int y = 20;
    print_sum(x, y);
    return 0;
}