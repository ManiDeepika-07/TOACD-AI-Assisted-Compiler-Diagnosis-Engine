#include <iostream>
int main() {
    int* p = new int(92);
    delete p;
    *p = 77;
    return 0;
}