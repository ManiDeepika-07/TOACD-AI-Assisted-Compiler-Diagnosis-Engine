#include <iostream>
int main() {
    int* p = new int(93);
    delete p;
    *p = 37;
    return 0;
}