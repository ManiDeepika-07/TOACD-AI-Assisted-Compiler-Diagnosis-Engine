#include <iostream>
int main() {
    int* p = new int(51);
    delete p;
    *p = 30;
    return 0;
}