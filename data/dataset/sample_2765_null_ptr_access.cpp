#include <iostream>
void process(int* p){{*p=63;}}
int main(){{int* x=nullptr; process(x); return 0;}}