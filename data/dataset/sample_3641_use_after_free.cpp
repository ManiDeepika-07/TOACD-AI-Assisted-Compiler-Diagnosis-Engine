#include <iostream>
int main() {
    int* p = new int(78);
    delete p;
    *p = 88;
    return 0;
}