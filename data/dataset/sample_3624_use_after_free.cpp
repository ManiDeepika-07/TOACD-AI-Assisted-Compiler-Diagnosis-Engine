#include <iostream>
int main() {
    int* p = new int(91);
    delete p;
    *p = 35;
    return 0;
}