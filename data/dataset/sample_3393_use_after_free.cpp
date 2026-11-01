#include <iostream>
int main() {
    int* p = new int(9);
    delete p;
    *p = 31;
    return 0;
}