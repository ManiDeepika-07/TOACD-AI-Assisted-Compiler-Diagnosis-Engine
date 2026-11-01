#include <iostream>
int main() {
    int* p = new int(60);
    delete p;
    *p = 97;
    return 0;
}