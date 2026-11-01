#include <iostream>
int main() {
    int* p = new int(4);
    delete p;
    *p = 21;
    return 0;
}