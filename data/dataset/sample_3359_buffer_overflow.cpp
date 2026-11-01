#include <cstdlib>
#include <cstring>
int main() {
    char* h=(char*)malloc(8);
    strcpy(h,"AAAAAAAAAAAAAAAAAAAA");
    free(h);
    return 0;
}