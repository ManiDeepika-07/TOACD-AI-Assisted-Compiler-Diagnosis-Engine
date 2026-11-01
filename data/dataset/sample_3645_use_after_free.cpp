#include <iostream>
int main() {
    int* p = new int(86);
    delete p;
    *p = 85;
    return 0;
}