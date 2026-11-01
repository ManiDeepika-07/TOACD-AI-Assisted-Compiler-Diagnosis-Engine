#include <iostream>
void process(int* p){{*p=70;}}
int main(){{int* x=nullptr; process(x); return 0;}}