#include <iostream>
int main() {
    int* p = new int(95);
    delete p;
    *p = 28;
    return 0;
}