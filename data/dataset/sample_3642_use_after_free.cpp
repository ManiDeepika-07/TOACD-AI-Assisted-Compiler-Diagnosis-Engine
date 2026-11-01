#include <iostream>
int main() {
    int* p = new int(45);
    delete p;
    *p = 91;
    return 0;
}