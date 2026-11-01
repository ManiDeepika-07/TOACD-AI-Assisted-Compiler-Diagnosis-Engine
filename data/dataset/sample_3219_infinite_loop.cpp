#include <iostream>
void handle(int x) {{ handle(x+1); }}
int main() {{ handle(34); return 0; }}