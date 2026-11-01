#include <iostream>
int main() {
    int* p = new int(57);
    delete p;
    *p = 49;
    return 0;
}