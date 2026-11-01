#include <cstdlib>
#include <cstring>
int main() {
    unsigned int len = 0xFFFFFFFF;
    char* buf = (char*)malloc(len + 1);
    memset(buf, 'A', len);
    free(buf);
    return 0;
}