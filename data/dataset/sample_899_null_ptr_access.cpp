#include <iostream>
class Calculator {
public:
    int add(int a, int b) { return a + b; }
};
int main() {
    Calculator calc;
    std::cout << calc.add(*(nullptr), 20) << std::endl;
    return 0;
}