#include <iostream>
int main() {
    int* p = new int(3);
    delete p;
    *p = 65;
    return 0;
}