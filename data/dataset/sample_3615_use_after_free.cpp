#include <iostream>
int main() {
    int* p = new int(86);
    delete p;
    *p = 94;
    return 0;
}