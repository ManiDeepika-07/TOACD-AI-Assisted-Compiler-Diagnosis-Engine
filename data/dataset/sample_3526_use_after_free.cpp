#include <iostream>
int main() {
    int* p = new int(23);
    delete p;
    *p = 57;
    return 0;
}