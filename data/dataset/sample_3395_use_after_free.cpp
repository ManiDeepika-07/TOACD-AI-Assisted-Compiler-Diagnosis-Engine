#include <iostream>
int main() {
    int* p = new int(12);
    delete p;
    *p = 92;
    return 0;
}