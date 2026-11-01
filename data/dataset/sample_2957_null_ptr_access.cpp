#include <iostream>
void process(int* p){{*p=2;}}
int main(){{int* x=nullptr; process(x); return 0;}}