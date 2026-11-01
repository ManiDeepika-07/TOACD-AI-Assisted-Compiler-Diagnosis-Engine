#include <cstdlib>
int main() {
    unsigned int len=0xFFFFFFFF;
    char* b=(char*)malloc(len+1);
    free(b);
    return 0;
}