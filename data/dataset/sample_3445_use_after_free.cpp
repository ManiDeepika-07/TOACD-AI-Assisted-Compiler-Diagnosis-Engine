#include <iostream>
int main() {
    int* p = new int(47);
    delete p;
    *p = 63;
    return 0;
}