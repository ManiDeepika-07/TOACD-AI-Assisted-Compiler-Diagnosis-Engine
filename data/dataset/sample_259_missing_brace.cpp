#include <iostream>
int main() 
    int* ptr = new int(10);
    std::cout << *ptr << std::endl;
    delete ptr;
    return 0;
}