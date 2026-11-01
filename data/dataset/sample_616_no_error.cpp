#include <iostream>
int main() {
    int sum = 0;
    for (int i = 0; i < 65; ++i) sum += i;
    std::cout << sum << std::endl;
    return 0;
}