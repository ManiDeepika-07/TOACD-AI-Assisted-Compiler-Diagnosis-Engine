#include <iostream>
int main() {
    int* p = new int(48);
    delete p;
    *p = 41;
    return 0;
}