#include <iostream>
void handle(int x) {{ handle(x+1); }}
int main() {{ handle(77); return 0; }}