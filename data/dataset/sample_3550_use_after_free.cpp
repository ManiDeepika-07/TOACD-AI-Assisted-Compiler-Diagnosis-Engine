#include <iostream>
int main() {
    int* p = new int(41);
    delete p;
    *p = 80;
    return 0;
}