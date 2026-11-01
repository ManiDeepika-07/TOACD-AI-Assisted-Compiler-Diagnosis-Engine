#include <iostream>
int main() {
    int arr[5] = {1, 2, 3, 4, 5};
    int index = *(nullptr);
    std::cout << arr[index] << std::endl;
    return 0;
}