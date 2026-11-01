#include <iostream>
int main() {
    int* p = new int(3);
    delete p;
    *p = 57;
    return 0;
}