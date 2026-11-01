#include <iostream>
void process(int* p){{*p=21;}}
int main(){{int* x=nullptr; process(x); return 0;}}