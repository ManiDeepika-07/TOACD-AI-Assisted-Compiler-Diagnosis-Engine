#include <iostream>
int main() {
    int* p = new int(15);
    delete p;
    *p = 30;
    return 0;
}