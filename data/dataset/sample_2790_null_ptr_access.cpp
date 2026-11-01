#include <iostream>
void process(int* p){{*p=86;}}
int main(){{int* x=nullptr; process(x); return 0;}}