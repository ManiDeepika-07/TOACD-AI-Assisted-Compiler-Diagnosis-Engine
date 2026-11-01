#include <iostream>
int main() {
    int* p = new int(64);
    delete p;
    *p = 10;
    return 0;
}