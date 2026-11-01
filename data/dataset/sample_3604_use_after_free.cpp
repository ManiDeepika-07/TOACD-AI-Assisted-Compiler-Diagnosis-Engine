#include <iostream>
int main() {
    int* p = new int(88);
    delete p;
    *p = 2;
    return 0;
}