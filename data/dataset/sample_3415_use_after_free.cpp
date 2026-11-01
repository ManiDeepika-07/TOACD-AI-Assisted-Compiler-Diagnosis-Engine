#include <iostream>
int main() {
    int* p = new int(70);
    delete p;
    *p = 37;
    return 0;
}