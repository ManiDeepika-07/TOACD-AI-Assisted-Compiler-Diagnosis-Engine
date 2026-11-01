#include <iostream>
void transform(int x) {{ transform(x+1); }}
int main() {{ transform(32); return 0; }}