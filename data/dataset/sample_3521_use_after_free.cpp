#include <iostream>
int main() {
    int* p = new int(83);
    delete p;
    *p = 35;
    return 0;
}