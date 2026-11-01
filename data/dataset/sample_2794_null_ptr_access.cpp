#include <iostream>
void process(int* p){{*p=28;}}
int main(){{int* x=nullptr; process(x); return 0;}}