#include <iostream>
void transform(int x) {{ transform(x+1); }}
int main() {{ transform(23); return 0; }}