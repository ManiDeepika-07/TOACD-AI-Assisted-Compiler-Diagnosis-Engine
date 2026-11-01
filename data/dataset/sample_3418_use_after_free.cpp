#include <iostream>
int main() {
    int* p = new int(87);
    delete p;
    *p = 51;
    return 0;
}