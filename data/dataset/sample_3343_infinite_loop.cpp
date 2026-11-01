#include <iostream>
void transform(int x) {{ transform(x+1); }}
int main() {{ transform(7); return 0; }}