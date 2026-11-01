#include <cstdlib>
#include <cstring>
int main() {
    char cmd[128];
    char arg[]="arg; rm -rf /";
    sprintf(cmd,"echo %s",arg);
    system(cmd);
    return 0;
}