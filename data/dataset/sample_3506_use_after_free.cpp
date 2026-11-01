#include <iostream>
int main() {
    int* p = new int(42);
    delete p;
    *p = 5;
    return 0;
}