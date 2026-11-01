#include <iostream>
int main() {
    int* p = new int(84);
    delete p;
    *p = 76;
    return 0;
}