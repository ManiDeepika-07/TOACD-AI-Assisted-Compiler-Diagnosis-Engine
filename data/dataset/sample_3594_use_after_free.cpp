#include <iostream>
int main() {
    int* p = new int(40);
    delete p;
    *p = 11;
    return 0;
}