#include <iostream>
int main() {
    int* p = new int(92);
    delete p;
    *p = 54;
    return 0;
}