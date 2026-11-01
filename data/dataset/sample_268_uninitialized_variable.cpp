#include <iostream>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    int val = var_uninit;
    std::cout << factorial(val) << std::endl;
    return 0;
}