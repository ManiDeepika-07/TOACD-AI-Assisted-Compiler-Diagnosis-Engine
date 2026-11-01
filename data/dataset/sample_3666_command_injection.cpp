#include <stdio.h>
int main() {
    char inp[64]="cat /etc/passwd";
    popen(inp,"r");
    return 0;
}