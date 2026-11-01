#include <iostream>
int main() {
    int* p = new int(55);
    delete p;
    *p = 96;
    return 0;
}