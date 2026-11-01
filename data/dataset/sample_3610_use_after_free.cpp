#include <iostream>
int main() {
    int* p = new int(36);
    delete p;
    *p = 66;
    return 0;
}