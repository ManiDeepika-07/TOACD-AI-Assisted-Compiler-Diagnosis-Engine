#include <iostream>
int main() {
    int* p = new int(18);
    delete p;
    *p = 52;
    return 0;
}