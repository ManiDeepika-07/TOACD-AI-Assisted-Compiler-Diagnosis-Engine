#include <iostream>
enum Color { RED, GREEN, BLUE };
int main() {
    Color c = RED;
    std::string s = c;
    std::cout << s << std::endl;
    return 0;
}