#include <iostream>
int main() {
    int* p = new int(64);
    delete p;
    *p = 13;
    return 0;
}