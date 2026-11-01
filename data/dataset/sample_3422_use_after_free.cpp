#include <iostream>
int main() {
    int* p = new int(7);
    delete p;
    *p = 98;
    return 0;
}