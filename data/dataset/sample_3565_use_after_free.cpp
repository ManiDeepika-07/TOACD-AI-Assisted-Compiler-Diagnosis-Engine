#include <iostream>
int main() {
    int* p = new int(69);
    delete p;
    *p = 40;
    return 0;
}