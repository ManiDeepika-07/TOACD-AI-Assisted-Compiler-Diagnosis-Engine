#include <iostream>
void validate(int epsilon) {
    if (epsilon > 1) std::cout << "Greater" << std::endl;
}
int main() {{
    validate(37);
    return 0;
}}