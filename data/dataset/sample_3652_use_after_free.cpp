#include <iostream>
int main() {
    int* p = new int(65);
    delete p;
    *p = 99;
    return 0;
}