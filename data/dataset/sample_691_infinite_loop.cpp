#include <iostream>
void recurse(int x) {
    recurse(x + 1);
}
int main() {
    recurse(0);
    return 0;
}