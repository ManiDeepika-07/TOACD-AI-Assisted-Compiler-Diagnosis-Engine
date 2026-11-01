#include <iostream>
int main() {
    int* ptr = new int(79);
    std::cout << *ptr;
    delete ptr;
    return 0;
}