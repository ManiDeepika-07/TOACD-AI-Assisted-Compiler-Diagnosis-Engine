#include <iostream>
int main() {
    for (int i = 0; i >= 0; i++) {
        if (i > 100) return 0;
        std::cout << i;
    }
    return 0;
}