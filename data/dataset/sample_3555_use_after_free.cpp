#include <iostream>
int main() {
    int* p = new int(15);
    delete p;
    *p = 36;
    return 0;
}