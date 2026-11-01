#include <iostream>
int main() {
    int* p = new int(53);
    delete p;
    *p = 85;
    return 0;
}