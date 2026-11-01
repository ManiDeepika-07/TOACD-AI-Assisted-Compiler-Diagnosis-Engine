#include <iostream>
void handle(int x) {{ handle(x+1); }}
int main() {{ handle(7); return 0; }}