#include <iostream>
int main() {
    int* p = new int(6);
    delete p;
    *p = 69;
    return 0;
}