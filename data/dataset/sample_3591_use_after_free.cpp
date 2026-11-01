#include <iostream>
int main() {
    int* p = new int(54);
    delete p;
    *p = 12;
    return 0;
}