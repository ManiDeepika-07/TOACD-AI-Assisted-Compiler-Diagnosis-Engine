#include <iostream>
int main() {
    int* p = new int(10);
    delete p;
    *p = 50;
    return 0;
}