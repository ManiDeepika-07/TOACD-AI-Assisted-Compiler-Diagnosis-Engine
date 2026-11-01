#include <iostream>
int main() {
    int* p = new int(77);
    delete p;
    *p = 46;
    return 0;
}