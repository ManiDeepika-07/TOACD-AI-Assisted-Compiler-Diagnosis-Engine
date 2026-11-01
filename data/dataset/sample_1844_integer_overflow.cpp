#include <iostream>
int shared_counter = 0;
void increment() {
    for (int i = 0; i < 1000; i++) {
        shared_counter++;
    }
}
int main() {
    increment();
    std::cout << shared_counter << std::endl;
    return 0;
}