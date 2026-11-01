#include <iostream>
int main() {
    int* p = new int(83);
    delete p;
    *p = 64;
    return 0;
}