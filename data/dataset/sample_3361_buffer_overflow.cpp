#include <cstdlib>
#include <cstring>
int main() {
    unsigned int len=0xFFFFFFFF;
    char* b=(char*)malloc(len+1);
    memset(b,'A',len);
    free(b);
    return 0;
}