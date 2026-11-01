#include <iostream>
int main() {
    int* p = new int(90);
    delete p;
    *p = 99;
    return 0;
}