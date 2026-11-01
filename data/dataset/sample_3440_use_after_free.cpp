#include <iostream>
int main() {
    int* p = new int(2);
    delete p;
    *p = 26;
    return 0;
}