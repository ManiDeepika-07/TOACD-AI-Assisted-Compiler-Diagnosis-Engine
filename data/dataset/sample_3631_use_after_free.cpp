#include <iostream>
int main() {
    int* p = new int(24);
    delete p;
    *p = 46;
    return 0;
}