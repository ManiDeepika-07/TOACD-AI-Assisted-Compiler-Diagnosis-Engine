#include <iostream>
int main() {
    int* p = new int(57);
    delete p;
    *p = 79;
    return 0;
}