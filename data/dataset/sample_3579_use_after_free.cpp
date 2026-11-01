#include <iostream>
int main() {
    int* p = new int(18);
    delete p;
    *p = 58;
    return 0;
}