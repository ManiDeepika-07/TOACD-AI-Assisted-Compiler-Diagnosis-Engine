#include <iostream>
int main() {
    int* p = new int(60);
    delete p;
    *p = 66;
    return 0;
}