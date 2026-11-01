#include <cstring>
#include <cstdlib>
#include <stdio.h>
int main() {
    char buf[8];
    strncpy(buf, "ABCDEFGH", 8);
    printf("%s\n", buf);
    return 0;
}