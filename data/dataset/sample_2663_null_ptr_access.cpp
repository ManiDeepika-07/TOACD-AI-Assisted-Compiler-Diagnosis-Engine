#include <iostream>
void process(int* p){{*p=1;}}
int main(){{int* x=nullptr; process(x); return 0;}}