#include <iostream>
int main() {
    int choice = 10;
    switch(choice) {
        case 1: std::cout << "One" << std::endl; break;
        default: std::cout << "Default" << std::endl; break;
    }
    return 0;
}