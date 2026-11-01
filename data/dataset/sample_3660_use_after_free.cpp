#include <iostream>
int main() {
    int* p = new int(85);
    delete p;
    *p = 22;
    return 0;
}