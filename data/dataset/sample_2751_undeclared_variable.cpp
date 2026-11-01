#include <iostream>
int main() {
    int choice = undeclared_var;
    switch(choice) {
        case 1: std::cout << "One" << std::endl; break;
        default: std::cout << "Default" << std::endl; break;
    }
    return 0;
}