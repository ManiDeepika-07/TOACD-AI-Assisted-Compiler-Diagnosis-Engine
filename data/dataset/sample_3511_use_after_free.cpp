#include <iostream>
int main() {
    int* p = new int(22);
    delete p;
    *p = 75;
    return 0;
}