#include <iostream>
int main() {
    int* p = new int(59);
    delete p;
    *p = 89;
    return 0;
}