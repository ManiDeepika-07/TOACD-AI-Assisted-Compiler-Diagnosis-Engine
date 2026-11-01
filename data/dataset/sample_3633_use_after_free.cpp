#include <iostream>
int main() {
    int* p = new int(55);
    delete p;
    *p = 25;
    return 0;
}