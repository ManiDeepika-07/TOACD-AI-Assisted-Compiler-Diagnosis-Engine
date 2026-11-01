#include <iostream>
int main() {
    int* p = new int(12);
    delete p;
    *p = 3;
    return 0;
}