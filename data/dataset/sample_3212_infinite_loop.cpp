#include <iostream>
void process(int x) {{ process(x+1); }}
int main() {{ process(50); return 0; }}