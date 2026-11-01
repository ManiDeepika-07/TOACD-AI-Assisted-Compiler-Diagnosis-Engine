#include <iostream>
int main() {
    int* p = new int(32);
    delete p;
    *p = 62;
    return 0;
}