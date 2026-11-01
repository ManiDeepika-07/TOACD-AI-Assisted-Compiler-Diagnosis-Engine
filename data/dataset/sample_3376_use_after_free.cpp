#include <iostream>
int main() {
    int* p = new int(92);
    delete p;
    *p = 74;
    return 0;
}