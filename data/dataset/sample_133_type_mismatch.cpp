#include <iostream>
int main() {
    int choice = "string";
    switch(choice) {
        case 1: std::cout << "One" << std::endl; break;
        default: std::cout << "Default" << std::endl; break;
    }
    return 0;
}