#include <iostream>
int main() {
    int* p = new int(91);
    delete p;
    *p = 43;
    return 0;
}