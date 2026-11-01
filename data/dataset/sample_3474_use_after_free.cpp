#include <iostream>
int main() {
    int* p = new int(23);
    delete p;
    *p = 54;
    return 0;
}