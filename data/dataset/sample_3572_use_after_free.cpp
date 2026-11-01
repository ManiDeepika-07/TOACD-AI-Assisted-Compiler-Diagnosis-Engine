#include <iostream>
int main() {
    int* p = new int(75);
    delete p;
    *p = 26;
    return 0;
}