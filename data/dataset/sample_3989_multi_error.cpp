#include <stdio.h>
#include <cstring>
int main() {
    char buf[8];
    char inp[64]="%x %x";
    strcpy(buf, "toolong");
    printf(inp);
    return 0;
}