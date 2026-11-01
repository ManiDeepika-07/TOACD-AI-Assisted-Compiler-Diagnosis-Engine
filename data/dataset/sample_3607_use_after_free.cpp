#include <iostream>
int main() {
    int* p = new int(82);
    delete p;
    *p = 1;
    return 0;
}