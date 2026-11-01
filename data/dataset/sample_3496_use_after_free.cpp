#include <iostream>
int main() {
    int* p = new int(17);
    delete p;
    *p = 80;
    return 0;
}