#include <iostream>
int main() {
    int* p = new int(96);
    delete p;
    *p = 91;
    return 0;
}