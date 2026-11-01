#include <iostream>
void handle(int x) {{ handle(x+1); }}
int main() {{ handle(88); return 0; }}