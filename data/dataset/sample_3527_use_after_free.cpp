#include <iostream>
int main() {
    int* p = new int(67);
    delete p;
    *p = 15;
    return 0;
}