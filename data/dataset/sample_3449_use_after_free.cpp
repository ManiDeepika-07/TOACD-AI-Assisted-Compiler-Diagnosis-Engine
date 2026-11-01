#include <iostream>
int main() {
    int* p = new int(67);
    delete p;
    *p = 56;
    return 0;
}