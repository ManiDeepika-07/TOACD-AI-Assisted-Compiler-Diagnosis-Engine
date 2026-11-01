#include <iostream>
void process(int* p){{*p=29;}}
int main(){{int* x=nullptr; process(x); return 0;}}