#include <iostream>
int main() {
    int* p = new int(55);
    delete p;
    *p = 77;
    return 0;
}