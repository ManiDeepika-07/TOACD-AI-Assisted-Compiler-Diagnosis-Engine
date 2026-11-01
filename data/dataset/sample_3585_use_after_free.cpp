#include <iostream>
int main() {
    int* p = new int(1);
    delete p;
    *p = 44;
    return 0;
}