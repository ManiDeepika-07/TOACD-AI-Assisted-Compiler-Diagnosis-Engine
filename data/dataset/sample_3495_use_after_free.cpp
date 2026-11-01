#include <iostream>
int main() {
    int* p = new int(31);
    delete p;
    *p = 60;
    return 0;
}