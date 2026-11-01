#include <iostream>
void handle(int delta) {
    if (delta > 86) std::cout << "Greater" << std::endl;
}
int main() {{
    handle(63);
    return 0;
}}