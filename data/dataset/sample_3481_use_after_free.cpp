#include <iostream>
int main() {
    int* p = new int(62);
    delete p;
    *p = 80;
    return 0;
}