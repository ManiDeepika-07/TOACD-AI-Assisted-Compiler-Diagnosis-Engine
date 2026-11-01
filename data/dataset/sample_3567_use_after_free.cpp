#include <iostream>
int main() {
    int* p = new int(33);
    delete p;
    *p = 82;
    return 0;
}