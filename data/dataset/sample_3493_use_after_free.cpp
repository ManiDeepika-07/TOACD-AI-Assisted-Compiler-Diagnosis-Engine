#include <iostream>
int main() {
    int* p = new int(40);
    delete p;
    *p = 19;
    return 0;
}