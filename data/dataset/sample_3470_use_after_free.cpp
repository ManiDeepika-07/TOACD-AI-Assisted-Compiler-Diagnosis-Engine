#include <iostream>
int main() {
    int* p = new int(78);
    delete p;
    *p = 17;
    return 0;
}