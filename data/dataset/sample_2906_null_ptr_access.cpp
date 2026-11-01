#include <iostream>
void process(int* p){{*p=67;}}
int main(){{int* x=nullptr; process(x); return 0;}}