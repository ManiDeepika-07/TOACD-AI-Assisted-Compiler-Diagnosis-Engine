#include <cstdlib>
int main() {
    int* p = (int*)malloc(sizeof(int));
    free(p);
    free(p);
    return 0;
}