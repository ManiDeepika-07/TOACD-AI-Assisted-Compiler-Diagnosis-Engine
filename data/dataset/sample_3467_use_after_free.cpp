#include <iostream>
int main() {
    int* p = new int(71);
    delete p;
    *p = 24;
    return 0;
}