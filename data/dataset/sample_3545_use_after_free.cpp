#include <iostream>
int main() {
    int* p = new int(94);
    delete p;
    *p = 87;
    return 0;
}