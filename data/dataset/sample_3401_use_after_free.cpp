#include <iostream>
int main() {
    int* p = new int(2);
    delete p;
    *p = 6;
    return 0;
}