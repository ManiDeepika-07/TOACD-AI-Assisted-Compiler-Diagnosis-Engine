#include <iostream>
int main() {
    int* p = new int(97);
    delete p;
    *p = 72;
    return 0;
}