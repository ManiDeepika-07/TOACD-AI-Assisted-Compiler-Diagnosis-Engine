#include <iostream>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    int val = "string";
    std::cout << factorial(val) << std::endl;
    return 0;
}