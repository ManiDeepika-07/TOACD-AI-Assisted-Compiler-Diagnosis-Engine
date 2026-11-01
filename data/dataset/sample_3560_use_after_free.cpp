#include <iostream>
int main() {
    int* p = new int(17);
    delete p;
    *p = 88;
    return 0;
}