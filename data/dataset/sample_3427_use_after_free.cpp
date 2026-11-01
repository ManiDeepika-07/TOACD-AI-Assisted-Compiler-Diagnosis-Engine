#include <iostream>
int main() {
    int* p = new int(42);
    delete p;
    *p = 84;
    return 0;
}