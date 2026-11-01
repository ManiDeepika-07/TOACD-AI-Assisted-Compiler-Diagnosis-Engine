#include <iostream>
int main() {
    int* p = new int(8);
    delete p;
    *p = 19;
    return 0;
}