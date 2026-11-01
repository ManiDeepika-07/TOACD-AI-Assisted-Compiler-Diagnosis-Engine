#include <iostream>
int main() {
    int* p = new int(19);
    delete p;
    *p = 39;
    return 0;
}