#include <iostream>
void process(int x) {{ process(x+1); }}
int main() {{ process(42); return 0; }}