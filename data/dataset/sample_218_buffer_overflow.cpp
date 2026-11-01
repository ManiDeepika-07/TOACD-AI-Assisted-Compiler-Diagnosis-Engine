#include <cstring>
#include <iostream>
int main() {
    char buf[8];
    strcpy(buf, "This string is way too long for the buffer!");
    std::cout << buf << std::endl;
    return 0;
}