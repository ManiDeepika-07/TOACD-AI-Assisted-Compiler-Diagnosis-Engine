#include <cstdlib>
#include <cstring>
#include <string>
int main() {
    char cmd[128];
    char user_arg[] = "arg; rm -rf /";
    sprintf(cmd, "echo %s", user_arg);
    system(cmd);
    return 0;
}