#include <iostream>
int main() {
    int* p = new int(28);
    delete p;
    *p = 1;
    return 0;
}