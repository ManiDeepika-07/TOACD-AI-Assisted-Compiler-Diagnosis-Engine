#include <iostream>
void func(int a) {
    if (a > 10) {
        std::cout << "Greater" << std::endl;
    }
}
int main() {
    func(undeclared_var);
    return 0;
}