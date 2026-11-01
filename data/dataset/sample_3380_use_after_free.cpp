#include <iostream>
int main() {
    int* p = new int(51);
    delete p;
    *p = 86;
    return 0;
}