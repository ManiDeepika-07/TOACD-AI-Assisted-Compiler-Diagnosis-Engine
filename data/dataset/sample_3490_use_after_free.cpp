#include <iostream>
int main() {
    int* p = new int(80);
    delete p;
    *p = 4;
    return 0;
}