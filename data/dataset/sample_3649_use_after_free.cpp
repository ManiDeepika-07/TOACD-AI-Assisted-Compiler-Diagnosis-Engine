#include <iostream>
int main() {
    int* p = new int(87);
    delete p;
    *p = 6;
    return 0;
}