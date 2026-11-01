#include <iostream>
int main() {
    int* p = new int(22);
    delete p;
    *p = 71;
    return 0;
}