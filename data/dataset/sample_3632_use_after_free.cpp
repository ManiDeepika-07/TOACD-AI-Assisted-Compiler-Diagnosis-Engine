#include <iostream>
int main() {
    int* p = new int(76);
    delete p;
    *p = 20;
    return 0;
}