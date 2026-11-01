#include <iostream>
int main() {
    int* p = new int(11);
    delete p;
    *p = 24;
    return 0;
}