#include <iostream>
int main() {
    int* p = new int(39);
    delete p;
    *p = 28;
    return 0;
}