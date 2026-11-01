#include <iostream>
char* getNum() {
    int num = 42;
    return num;
}
int main() {
    std::cout << getNum() << std::endl;
    return 0;
}