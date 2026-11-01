#include <iostream>
int main() {
    int* p = new int(62);
    delete p;
    *p = 55;
    return 0;
}