#include <iostream>
int main() {
    int* p = new int(88);
    delete p;
    *p = 78;
    return 0;
}