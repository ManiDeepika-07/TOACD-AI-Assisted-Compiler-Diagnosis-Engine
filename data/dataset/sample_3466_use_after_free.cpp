#include <iostream>
int main() {
    int* p = new int(36);
    delete p;
    *p = 77;
    return 0;
}