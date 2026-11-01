#include <iostream>
int main() {
    int* p = new int(80);
    delete p;
    *p = 94;
    return 0;
}