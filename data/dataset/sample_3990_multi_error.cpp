#include <cstring>
int main() {
    char buf[4];
    while(true) {{
        strcpy(buf, "overflow");
    }}
    return 0;
}