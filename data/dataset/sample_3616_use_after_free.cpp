#include <iostream>
int main() {
    int* p = new int(73);
    delete p;
    *p = 70;
    return 0;
}