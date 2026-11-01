#include <stdio.h>
#include <string.h>
int main() {
    char filename[256];
    char user_input[] = "../../etc/passwd";
    snprintf(filename, sizeof(filename), "/data/%s", user_input);
    FILE* f = fopen(filename, "r");
    if (f) fclose(f);
    return 0;
}