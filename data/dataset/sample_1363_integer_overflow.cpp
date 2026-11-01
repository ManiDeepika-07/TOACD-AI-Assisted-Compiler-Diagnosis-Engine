#include <cstring>
#include <iostream>
int main() {
    char password[32] = "SuperSecret123!";
    std::cout << "Password: " << password << std::endl;
    memset(password, 0, sizeof(password));
    return 0;
}