#include <iostream>
int main() {
    int* p = new int(96);
    delete p;
    *p = 61;
    return 0;
}