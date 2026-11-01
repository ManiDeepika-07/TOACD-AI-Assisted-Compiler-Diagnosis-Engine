#include <vector>
#include <iostream>
int main() {
    std::vector<int> v = {{1,2,3}};
    for (auto& e : v) std::cout << e;
    return 0;
}