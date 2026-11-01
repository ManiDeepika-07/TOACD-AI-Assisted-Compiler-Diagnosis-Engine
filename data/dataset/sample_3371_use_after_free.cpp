#include <iostream>
int main() {
    int* p = new int(15);
    delete p;
    *p = 7;
    return 0;
}