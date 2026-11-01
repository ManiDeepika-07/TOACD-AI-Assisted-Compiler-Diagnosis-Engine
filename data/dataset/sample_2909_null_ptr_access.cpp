#include <iostream>
void execute(int* p){{*p=80;}}
int main(){{int* x=nullptr; execute(x); return 0;}}