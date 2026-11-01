#include <iostream>
int main() {
    int* p = new int(16);
    delete p;
    *p = 95;
    return 0;
}