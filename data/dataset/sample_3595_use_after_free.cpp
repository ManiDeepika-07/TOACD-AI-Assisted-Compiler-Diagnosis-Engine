#include <iostream>
int main() {
    int* p = new int(15);
    delete p;
    *p = 66;
    return 0;
}