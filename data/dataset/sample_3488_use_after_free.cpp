#include <iostream>
int main() {
    int* p = new int(32);
    delete p;
    *p = 5;
    return 0;
}