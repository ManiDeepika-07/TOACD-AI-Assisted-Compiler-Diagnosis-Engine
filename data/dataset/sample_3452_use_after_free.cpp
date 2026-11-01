#include <iostream>
int main() {
    int* p = new int(30);
    delete p;
    *p = 98;
    return 0;
}