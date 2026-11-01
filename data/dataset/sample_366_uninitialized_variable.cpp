#include <iostream>
int main() {
    int sum = 0;
    for (int i = 0; i < var_uninit; ++i) {
        sum += i;
    }
    std::cout << sum << std::endl;
    return 0;
}